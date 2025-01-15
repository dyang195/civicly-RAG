"""
Core search functionality implementation.
Vector search, query enhancement, result processing, and summary generation.
"""

import time
import redis
import openai
from datetime import datetime

from models import SearchQuery, SearchResult, SearchResponse
from vector_store import VectorStore
from config import settings

class SearchService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.redis_client = redis.from_url(settings.REDIS_URL)
        openai.api_key = settings.OPENAI_API_KEY

    async def search(self, search_query: SearchQuery) -> SearchResponse:
        start_time = time.time()
        
        # Enhance query with llm generated keywords
        enhanced_query = await self._enhance_query(search_query.query)

        # Semantic search on vector store
        results = await self.vector_store.search(
            enhanced_query,
            limit=search_query.limit
        )

        search_results = [
            SearchResult(
                event_id=result.metadata["annotation_event_id"],
                text=result.metadata["text"],
                meeting_date=result.metadata["session_date"],
                meeting_title=result.metadata["annotation_meeting_name"],
                speaker=result.metadata["speaker"],
                relevance_score=result.score,
                start_time=result.metadata["start_time"],
                end_time=result.metadata["end_time"]
            )
            for result in results
        ]

        # Generate llm summary
        summary = await self._generate_summary(search_results, search_query.query)
        
        return SearchResponse(
            results=search_results,
            total_results=len(search_results),
            processing_time=time.time() - start_time,
            summary=summary
        )

    async def _enhance_query(self, query: str, city: str = "seattle") -> str:
        cache_key = f"enhanced_query:{query}"
        
        if cached := self.redis_client.get(cache_key):
            return cached.decode()

        system_prompt = f"""You are a query enhancement system for semantic search of {city} city council transcripts.
        Your task is to enhance queries by adding relevant context and related terms that would appear in the same
        chunks of text as the user's search intent. Focus on natural language rather than boolean operators.

        Guidelines:
        - Add synonyms and related terms that commonly appear together in government documents
        - Include relevant government process terms
        - Keep language natural and conversational like it would appear in meeting minutes
        - Do not use boolean operators or special formatting

        Format your response as a simple natural language sentence that expands on the query.

        Examples:
        User: bike lanes
        Response: bike lanes protected bike lanes bicycle safety bike infrastructure bicycle commuting

        User: what are they doing about climate change in the city
        Response: climate action plan greenhouse gas emissions green new deal building electrification clean energy goals carbon neutral city environmental sustainability electric vehicle charging climate resilience

        User: I'm a tech worker moving to Seattle, what should I know about
        Response: South Lake Union tech campus development Amazon office expansion transit options commuter benefits transportation infrastructure remote work policies housing affordability tech industry impact

        User: can you tell me about efforts to help homeless people downtown
        Response: downtown homeless services shelter capacity permanent supportive housing outreach teams urban rest stop hygiene centers tiny house villages union station shelter downtown emergency service center

        User: looking for information about construction and development in my area
        Response: construction permits design review board land use notifications zoning changes neighborhood planning development standards impact fees public comment period SEPA review"""

        try:
            completion = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"{system_prompt}"},
                    {"role": "user", "content": f"{query}"}
                ]
            )
            enhanced = completion.choices[0].message.content
            self.redis_client.setex(cache_key, 3600, enhanced)
            return enhanced
        except Exception as e:
            print(f"Query enhancement failed: {e}")
            return query

    async def _generate_summary(self, results: list[SearchResult], original_query: str) -> str:
        """Generate a concise summary of search results."""
        if not results:
            return "No relevant results found."

        cache_key = f"summary:{original_query}"
        if cached := self.redis_client.get(cache_key):
            return cached.decode()

        current_date = datetime.now().strftime("%Y-%m-%d")
        context = f"Current date: {current_date}\n\n"
        
        for result in results:
            context += f"Meeting: {result.meeting_title} (Date: {result.meeting_date})\n"
            context += f"Text: {result.text}\n\n"

        system_prompt = """You are a city council transcript summarization system. Create a brief, succinct, informative summary 
        of the search results that captures the key points discussed in the provided transcript segments. 
        
        Guidelines:
        - Focus on the most recent and relevant information first
        - If there's a clear timeline of events or policy evolution, reflect that in the summary
        - If multiple meetings discuss the same topic, note any significant changes or progress
        - Keep the summary concise (2-3 sentences and around 50 words) while preserving key details
        - Mention specific meeting dates only if they're particularly relevant to the topic
        - Just return the summary text itself, no need for formatting
        - Don't include the current date in the response, just use it to orient your answers temporally"""

        try:
            completion = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Original query: {original_query}\n\nRelevant transcript segments:\n{context}"}
                ]
            )
            summary = completion.choices[0].message.content
            self.redis_client.setex(cache_key, 3600, summary)
            return summary
        except Exception as e:
            print(f"Summary generation failed: {e}")
            return "Summary generation failed. Please review the individual results."