"""
Pydantic models for the backend.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SearchQuery(BaseModel):
    query: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: Optional[int] = 10

class SearchResult(BaseModel):
    event_id: str
    text: str
    meeting_date: datetime
    meeting_title: str
    speaker: str
    relevance_score: float
    start_time: str
    end_time: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int
    processing_time: float
    summary: str
