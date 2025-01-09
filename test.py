from cdp_backend.database import models as db_models
from cdp_backend.pipeline.transcript_model import Transcript
import fireo
from gcsfs import GCSFileSystem
from google.auth.credentials import AnonymousCredentials
from google.cloud.firestore import Client
from datetime import datetime
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import chromadb
from chromadb.config import Settings

def format_time(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def print_transcript(transcript: Transcript) -> None:
    """Print transcript in a legible format"""
    # Print header information
    print("=" * 80)
    print(f"Transcript Details:")
    print(f"Generator: {transcript.generator}")
    print(f"Confidence: {transcript.confidence:.2f}")
    if transcript.session_datetime:
        session_dt = datetime.fromisoformat(transcript.session_datetime)
        print(f"Session Date: {session_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Created: {datetime.fromisoformat(transcript.created_datetime).strftime('%Y-%m-%d %H:%M:%S')}")
    if transcript.annotations:
        print("\nTranscript Annotations:")
        for key, value in transcript.annotations.__dict__.items():
            if value is not None:
                print(f"  - {key}: {value}")
    print("=" * 80)
    print()

    # Print sentences
    for sentence in transcript.sentences:
        # Print timestamp and speaker info
        timestamp = f"[{format_time(sentence.start_time)} - {format_time(sentence.end_time)}]"
        speaker = f"Speaker {sentence.speaker_index}" if sentence.speaker_index is not None else ""
        speaker_name = f"({sentence.speaker_name})" if sentence.speaker_name else ""
        
        print(f"{speaker} {speaker_name}")
        print(f"Text: {sentence.text}")
        
        # Print any sentence annotations if they exist
        if sentence.annotations:
            print("Annotations:")
            for key, value in sentence.annotations.__dict__.items():
                if value is not None:
                    print(f"  - {key}: {value}")
        
        print("-" * 80)

# Connect to the database
fireo.connection(client=Client(
    project="cdp-seattle-21723dcf",
    credentials=AnonymousCredentials()
))

# Read from the database
# five_people = list(db_models.Person.collection.fetch(100))
# print(len(five_people))
# for person in five_people:
#     print(f"Name: {person.name}")
#     print(f"Email: {person.email}")
#     print(f"Phone: {person.phone}")
#     print("-" * 30)


# # Connect to the file store
# fs = GCSFileSystem(project="cdp-seattle-21723dcf", token="anon")

# # Read a transcript's details from the database
# transcript_model = list(db_models.Transcript.collection.fetch(1))[0]
# thing = transcript_model.session_ref.get().event_ref.get().id
# print(thing)

# # Read the transcript directly from the file store
# with fs.open(transcript_model.file_ref.get().uri, "r") as open_resource:
#     transcript = Transcript.from_json(open_resource.read())
#     print_transcript(transcript)

# # OR download and store the transcript locally with `get`
# fs.get(transcript_model.file_ref.get().uri, "local-transcript.json")
# # Then read the transcript from your local machine
# with open("local-transcript.json", "r") as open_resource:
#     transcript = Transcript.from_json(open_resource.read())
#     print(transcript)


class TranscriptChunk:
    def __init__(self, text: str, metadata: Dict):
        self.text = text
        self.metadata = metadata

class TranscriptRAG:
    def __init__(self, chunk_size: int = 500):
        self.chunk_size = chunk_size
        # Initialize sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            persist_directory="./transcript_db"
        ))
        self.collection = self.chroma_client.create_collection(name="transcripts")

    def process_transcript(self, transcript: Transcript) -> List[TranscriptChunk]:
        """Process a transcript into chunks with metadata"""
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in transcript.sentences:
            # Create rich metadata for each chunk
            metadata = {
                'start_time': sentence.start_time,
                'end_time': sentence.end_time,
                'speaker': sentence.speaker_name or f"Speaker {sentence.speaker_index}" if sentence.speaker_index else "Unknown",
                'confidence': sentence.confidence,
                'session_date': transcript.session_datetime,
                'generator': transcript.generator
            }
            
            # Add any custom annotations
            if sentence.annotations:
                for key, value in sentence.annotations.__dict__.items():
                    if value is not None:
                        metadata[f"annotation_{key}"] = str(value)

            # Chunk based on size while preserving sentence boundaries
            if current_length + len(sentence.text) > self.chunk_size and current_chunk:
                chunks.append(TranscriptChunk(
                    text=' '.join(current_chunk),
                    metadata=metadata
                ))
                current_chunk = []
                current_length = 0
            
            current_chunk.append(sentence.text)
            current_length += len(sentence.text)
        
        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(TranscriptChunk(
                text=' '.join(current_chunk),
                metadata=metadata
            ))
        
        return chunks

    def index_transcript(self, transcript: Transcript):
        """Index a transcript into the vector database"""
        chunks = self.process_transcript(transcript)
        
        # Prepare data for ChromaDB
        texts = [chunk.text for chunk in chunks]
        embeddings = self.model.encode(texts)
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [f"chunk_{i}_{datetime.datetime.now().timestamp()}" for i in range(len(chunks))]
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    def semantic_search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search through transcripts using semantic similarity"""
        # Encode query
        query_embedding = self.model.encode(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'similarity_score': 1 - results['distances'][0][i]  # Convert distance to similarity
            })
            
        return formatted_results

    def concept_based_search(self, concept_query: str) -> List[Dict]:
        """
        Enhanced search that understands high-level concepts
        Example: "meetings useful to a 24 yr old in tech"
        """
        # You could enhance this with additional context and rules
        tech_keywords = [
            "technology", "software", "digital", "innovation", "startup",
            "development", "programming", "infrastructure", "data",
            "applications", "platforms", "systems"
        ]
        
        # Expand the original query with relevant context
        expanded_query = f"""
        {concept_query}
        Context: Looking for discussions about {', '.join(tech_keywords)},
        city development affecting young professionals,
        innovation initiatives, startup support,
        tech industry growth, digital infrastructure
        """
        
        return self.semantic_search(expanded_query, n_results=5)

# Usage example:
def main():
    # Initialize the RAG system
    rag = TranscriptRAG()
    
    # Index multiple transcripts
    # transcript_files = ["transcript1.json", "transcript2.json"]  # Add your transcript files
    # for file_path in transcript_files:
    #     with open(file_path, "r") as f:
    #         transcript = Transcript.from_json(f.read())
    #         rag.index_transcript(transcript)

    fs = GCSFileSystem(project="cdp-seattle-21723dcf", token="anon")

    # Read a transcript's details from the database
    transcript_models = list(db_models.Transcript.collection.fetch(100))
    
    ids = [(transcript_model.session_ref.get().event_ref.get().id, transcript_model.session_ref.get().event_ref.get().body_ref.get().name) for transcript_model in transcript_models]
    print(ids)
    
    for transcript_model in transcript_models:
        # Read the transcript directly from the file store
        with fs.open(transcript_model.file_ref.get().uri, "r") as open_resource:
            transcript = Transcript.from_json(open_resource.read())
            rag.index_transcript(transcript)

    # Example searches
    concept_query = "meetings useful to a 24 yr old in tech"
    results = rag.concept_based_search(concept_query)
    
    print(f"\nSearch Results for: {concept_query}")
    print("=" * 80)
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Text: {result['text']}")
        print(f"Session Date: {result['metadata']['session_date']}")
        print(f"Speaker: {result['metadata']['speaker']}")
        print(f"Similarity Score: {result['similarity_score']:.2f}")
        print("-" * 40)

if __name__ == "__main__":
    main()
