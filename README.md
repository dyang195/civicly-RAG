# Civicly.ai

A Visual Studio Code extension that provides AI-powered search and summarization for city council records, making local government more accessible and understandable. The platform uses semantic search and AI summarization to help citizens easily find and comprehend information from city council meetings.

## Features

- **Semantic Search**: Vector-based search that understands context and meaning, not just keywords
- **LLM Query Enhancement**: Automatically expands search queries with relevant government and policy terms
- **Search Summarization**: Generates concise, temporal-aware summaries of search results
- **City Council Records**: Currently supporting Seattle City Council records

## Technical Implementation

### Backend Architecture

- **Framework**: FastAPI
- **Vector Datavase**: Pinecone vector database with sentence-transformers
- **AI Integration**: OpenAI GPT-4o-mini for query enhancement and summarization
- **Caching**: Redis for performance optimization
- **Vector Embeddings**: MiniLM-L6-v2 model for semantic search embeddings

## Development

The project uses FastAPI for the backend with several key components:

- `SearchService`: Core search implementation with vector search and AI enhancement
- `VectorStore`: Pinecone database interface for semantic search
- `Models`: Pydantic models for type-safe data handling
- `Config`: Environment and settings management

Testing can be run using the included test script:
```bash
python test_script.py
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/civicly-ai.git
cd civicly-ai
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Start the server:
```bash
uvicorn main:app --reload
```

### Environment Variables

```
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
REDIS_URL=redis://localhost:6379
```

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.