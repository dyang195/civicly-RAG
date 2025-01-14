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
        print(results)
        # Format results
        search_results = [
            SearchResult(
                text=result.metadata["text"],
                meeting_date= result.metadata["session_date"],
                meeting_title= "title1", # result.metadata["meeting_title"],
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

    async def _enhance_query(self, query: str) -> str:
        cache_key = f"enhanced_query:{query}"
        
        if cached := self.redis_client.get(cache_key):
            return cached.decode()

        try:
            completion = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Enhance this search query for searching city council transcripts."},
                    {"role": "user", "content": f"Query: {query}"}
                ]
            )
            enhanced = completion.choices[0].message.content
            self.redis_client.setex(cache_key, 3600, enhanced)
            return enhanced
        except Exception as e:
            print(f"Query enhancement failed: {e}")
            return query