"""
Vector database interface for semantic search functionality.
"""

import pinecone
from typing import List
from sentence_transformers import SentenceTransformer

from config import settings

class VectorStore:
    def __init__(self):
        _pc = pinecone.Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = _pc.Index("council-transcripts")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')


    def _text_to_vector(self, text: str) -> List[float]:
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    async def search(self, query: str, limit: int = 10):
        query_vector = self._text_to_vector(query)
        
        results = self.index.query(
            namespace="seattle",
            vector=query_vector,
            top_k=limit,
            include_metadata=True
        )
        
        return results.matches
        