import os
import asyncio
from app.rag.embeddings import GeminiEmbedding
from app.rag.retriever import QdrantRetriever

async def ingest_data():
    print("Starting data ingestion...")
    
    # Path settings
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, "data", "book.txt")
    
    if not os.path.exists(data_path):
        print(f"Error: File not found at {data_path}")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Chunks banayein (1000 characters each)
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    print(f"Loaded {len(chunks)} chunks from book.txt")

    embeddings = GeminiEmbedding()
    
    # Use context manager correctly
    async with QdrantRetriever(embedding_client=embeddings) as retriever:
        await retriever.upsert_documents(chunks)

    print("--- DATA INGESTION COMPLETED SUCCESSFULLY ---")

if __name__ == "__main__":
    asyncio.run(ingest_data())