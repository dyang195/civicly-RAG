"""
Test script to play around w/ for backend functionality.
"""

import asyncio
from search_service import SearchService
from models import SearchQuery
from vector_store import VectorStore

async def test_search():
    """Test search functionality"""
    service = SearchService()
    
    # Test basic search
    query = SearchQuery(query="sustainability efforts")
    results = await service.search(query)
    print("\n=== Basic Search Results ===")
    for i, result in enumerate(results.results, 1):
        print(f"\nResult {i}: {result}")
        print(f"Text: {result.text[:200]}...")
        print(f"Meeting: {result.meeting_title}")
        print(f"Date: {result.meeting_date}")
        print(f"Speaker: {result.speaker}")
        print(f"Score: {result.relevance_score}")

async def test_query_enhancement():
    """Test GPT query enhancement"""
    service = SearchService()
    
    test_queries = [
        "bikes",
        "environmental protection",
        "housing development"
    ]
    
    print("\n=== Query Enhancement Tests ===")
    for query in test_queries:
        enhanced = await service._enhance_query(query)
        print(f"\nOriginal: {query}")
        print(f"Enhanced: {enhanced}")

async def test_vector_search():
    """Test vector search directly"""
    store = VectorStore()
    
    test_query = "public transportation improvements"
    results = await store.search(test_query, limit=3)
    
    print("\n=== Vector Search Results ===")
    for i, result in enumerate(results, 1):
        print(f"\nMatch {i}:")
        print(f"Score: {result.score}")
        print(f"Metadata: {result.metadata}")

async def main():
    """Run all tests"""
    print("Starting manual tests...")
    
    try:
        await test_search()
    except Exception as e:
        print(f"Search test failed: {e}")
    
    try:
        await test_query_enhancement()
    except Exception as e:
        print(f"Query enhancement test failed: {e}")
    
    try:
        await test_vector_search()
    except Exception as e:
        print(f"Vector search test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())