from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.rag.ingest import ingest_data
from app.db.sqlite import create_db_and_tables

# Create a FastAPI app instance
app = FastAPI(
    title="RAG Chatbot Backend",
    description="A production-ready RAG chatbot backend using FastAPI and Gemini.",
    version="1.0.0",
)

@app.on_event("startup")
def on_startup():
    """
    Event handler for application startup.
    - Creates the database and tables for chat history.
    - Ingests data into the vector store.
    """
    print("Application starting up...")
    
    # 1. Create SQLite database and tables
    print("Initializing database...")
    create_db_and_tables()
    print("Database initialized.")
    
    # 2. Ingest data into the in-memory Qdrant.
    # For a production setup with a persistent Qdrant, you would run
    # this ingestion as a separate, one-time script, not on startup.
    print("Ingesting data into vector store...")
    ingest_data()
    print("Data ingestion complete.")
    
    print("Startup complete.")

# Include the chat router
app.include_router(chat_router, prefix="/api", tags=["Chat"])

@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint to check if the server is running.
    """
    return {"message": "Welcome to the RAG Chatbot API!"}
