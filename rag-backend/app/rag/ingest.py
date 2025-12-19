import os
import sys
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.embeddings import GeminiEmbedding
from app.rag.retriever import QdrantRetriever

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def ingest_data():
    """
    Loads data from a file, chunks it, and upserts it into the Qdrant collection.
    """
    print("Starting data ingestion...")

    # Define the path to the book data
    data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'book.txt')

    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return

    print(f"Loading data from {data_path}...")
    with open(data_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Chunk the text
    print("Chunking text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    print(f"Created {len(chunks)} chunks.")

    # Get the embedding and retriever clients
    print("Initializing embedding and retriever clients...")
    embedding_client = GeminiEmbedding()
    retriever = QdrantRetriever(embedding_client=embedding_client)

    # Upsert the documents into Qdrant
    print("Upserting documents into Qdrant...")
    retriever.upsert_documents(chunks)

    print("Data ingestion completed successfully!")

if __name__ == "__main__":
    ingest_data()
