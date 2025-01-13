"""
Vector database interface for semantic search functionality.
"""

import pinecone
from typing import List
from sentence_transformers import SentenceTransformer

from config import settings

class VectorStore:
    def __init__(self):
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        self.index = pinecone.Index("council-transcripts")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')


    def _text_to_vector(self, text: str) -> List[float]:
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    async def search(self, query: str, limit: int = 10):
        query_vector = self._text_to_vector(query)
        
        results = self.index.query(
            vectore=query_vector,
            top_k=limit,
            include_metadata=True
        )
        
        return results.matches
        