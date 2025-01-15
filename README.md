# Civicly.ai

[Civicly.ai](https://civicly.ai) is a website that provides AI-powered search and summarization for city council records, making local government more accessible and understandable. The web application uses semantic search and AI summarization to help citizens easily find and comprehend information from city council meetings.

## Features

- **Semantic Search**: Vector-based search that understands context and meaning, not just keywords
- **LLM Query Enhancement**: Automatically expands search queries with relevant government and policy terms
- **Search Summarization**: Generates concise, temporal-aware summaries of search results
- **City Council Records**: Currently supporting Seattle City Council records

## Technical Implementation

### Frontend Architecture

- **Framework**: Next.js (Node.js)
- **Hosting**: Vercel
- **UI**: React

### Backend Architecture

- **Framework**: FastAPI
- **Hosting**: Railway.app
- **Vector Database**: Pinecone.io
- **LLM Provider**: OpenAI GPT-4o-mini
- **Data Source**: Council Data Project
- **Vector Embeddings**: MiniLM-L6-v2

## Get Started

### Backend Development

The project uses FastAPI for the backend with several key components:

- `SearchService`: Core search implementation with vector search and AI enhancement
- `VectorStore`: Pinecone database interface for semantic search
- `Models`: Pydantic models for type-safe data handling
- `Config`: Environment and settings management

#### Backend Installation

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

#### Backend Environment Variables

```
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
REDIS_URL=redis://localhost:6379
```

### Frontend Development

The frontend is built with Next.js and React, providing a modern and responsive user interface.

#### Frontend Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your API endpoints and keys
```

4. Start the development server:
```bash
npm run dev
# or
yarn dev
```

The frontend will be available at `http://localhost:3000`.

#### Frontend Environment Variables

```
NEXT_PUBLIC_API_URL=your_backend_url
```

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.