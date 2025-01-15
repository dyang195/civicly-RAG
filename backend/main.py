"""
Backend API entrypoint, defines endpoints and handles HTTP requests.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import SearchQuery, SearchResponse
from search_service import SearchService
from config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search", response_model=SearchResponse)
async def search_transcripts(query: SearchQuery):
    search_service = SearchService()
    return await search_service.search(query)
