"""
Backend API entrypoint, defines endpoints and handles HTTP requests.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import SearchQuery, SearchResponse
from search_service import SearchService
from config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://www.civicly.ai",
        "https://civicly-ai.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search", response_model=SearchResponse)
async def search_transcripts(query: SearchQuery):
    search_service = SearchService()
    return await search_service.search(query)

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)