"""
Core search functionality implementation.
Vector search, query enhancement, and result processing.
"""

import time
import redis
import openai

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
        
        # Enhance query with GPT
        enhanced_query = await self._enhance_query(search_query.query)
        # Search vectors
        results = await self.vector_store.search(
            enhanced_query,
            limit=search_query.limit
        )
        # Format results
        search_results = [
            SearchResult(
                event_id=result.metadata["annotation_event_id"],
                text=result.metadata["text"],
                meeting_date= result.metadata["session_date"],
                meeting_title= result.metadata["annotation_meeting_name"],
                speaker=result.metadata["speaker"],
                relevance_score=result.score,
                start_time=result.metadata["start_time"],
                end_time=result.metadata["end_time"]
            )
            for result in results
        ]
        
        return SearchResponse(
            results=search_results,
            total_results=len(search_results),
            processing_time=time.time() - start_time
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