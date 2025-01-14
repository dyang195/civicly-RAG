import os
import time
from dotenv import load_dotenv
from cdp_backend.database import models as db_models
from cdp_backend.pipeline.transcript_model import Transcript
import fireo
from gcsfs import GCSFileSystem
from google.auth.credentials import AnonymousCredentials
from google.cloud.firestore import Client
from datetime import datetime
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from tqdm import tqdm

class TranscriptChunk:
    def __init__(self, text: str, metadata: Dict):
        self.text = text
        self.metadata = metadata

class TranscriptIndexer:
    def __init__(self, chunk_size: int = 500):
        # Load environment variables
        load_dotenv()
        
        self.chunk_size = chunk_size
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Pinecone with serverless config
        self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        
        # Create index if it doesn't exist
        self.index_name = "council-transcripts"
        try:
            # Try to get the index
            self.index = self.pc.Index(self.index_name)
        except Exception:
            # If index doesn't exist, create it
            print(f"Creating new index: {self.index_name}")
            dimension = 384  # all-MiniLM-L6-v2 outputs 384 dimensions
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-west-2"  # or your preferred region
                )
            )
            
            # Wait for index to be ready
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)
            
            self.index = self.pc.Index(self.index_name)
        
        # Initialize CDP connections
        self.fs = GCSFileSystem(project="cdp-seattle-21723dcf", token="anon")
        fireo.connection(client=Client(
            project="cdp-seattle-21723dcf",
            credentials=AnonymousCredentials()
        ))

    def process_transcript(self, transcript: Transcript) -> List[TranscriptChunk]:
        """Process a transcript into chunks with metadata"""
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in transcript.sentences:
            metadata = {
                'start_time': str(sentence.start_time),
                'end_time': str(sentence.end_time),
                'speaker': sentence.speaker_name or f"Speaker {sentence.speaker_index}" if sentence.speaker_index else "Unknown",
                'confidence': float(sentence.confidence),
                'session_date': transcript.session_datetime,
                'generator': transcript.generator
            }
            
            # Add custom annotations
            if sentence.annotations:
                for key, value in sentence.annotations.__dict__.items():
                    if value is not None:
                        metadata[f"annotation_{key}"] = str(value)

            if current_length + len(sentence.text) > self.chunk_size and current_chunk:
                chunks.append(TranscriptChunk(
                    text=' '.join(current_chunk),
                    metadata=metadata
                ))
                current_chunk = []
                current_length = 0
            
            current_chunk.append(sentence.text)
            current_length += len(sentence.text)
        
        if current_chunk:
            chunks.append(TranscriptChunk(
                text=' '.join(current_chunk),
                metadata=metadata
            ))
        
        return chunks

    def index_transcript(self, transcript: Transcript, namespace: str = "default"):
        """Index a transcript into Pinecone"""
        chunks = self.process_transcript(transcript)
        
        # Prepare vectors for batch upsert
        vectors = []
        for i, chunk in enumerate(chunks):
            # Generate embedding using SentenceTransformer
            vector = self.model.encode(chunk.text).tolist()
            
            # Add metadata and create vector record
            vectors.append({
                'id': f"chunk_{datetime.now().timestamp()}_{i}",
                'values': vector,
                'metadata': {
                    **chunk.metadata,
                    'text': chunk.text  # Store the original text in metadata
                }
            })
        
        # Upsert vectors in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(
                vectors=batch,
                namespace=namespace
            )

    def index_multiple_transcripts(self, limit: int = 10, namespace: str = "default"):
        """Index multiple transcripts from CDP"""
        print(f"Fetching {limit} transcripts from CDP...")
        transcript_models = list(db_models.Transcript.collection.fetch(limit))
        
        print("Processing and indexing transcripts...")
        for transcript_model in tqdm(transcript_models):
            try:
                # Read transcript from GCS
                with self.fs.open(transcript_model.file_ref.get().uri, "r") as open_resource:
                    transcript = Transcript.from_json(open_resource.read())
                    
                    # Add event metadata
                    event = transcript_model.session_ref.get().event_ref.get()
                    body = event.body_ref.get()
                    
                    # Add additional metadata to transcript
                    transcript.annotations = transcript.annotations or type('obj', (), {})()
                    transcript.annotations.event_id = event.id
                    transcript.annotations.body_name = body.name
                    
                    # Index the transcript
                    self.index_transcript(transcript, namespace=namespace)
                    
            except Exception as e:
                print(f"Error processing transcript: {e}")
                continue

def main():
    # Initialize indexer
    indexer = TranscriptIndexer()
    
    # Index transcripts
    indexer.index_multiple_transcripts(
        limit=10,  # Adjust limit as needed
        namespace="seattle"  # You can organize by city/region
    )
    
    print("Indexing complete!")

if __name__ == "__main__":
    main()