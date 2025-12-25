from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # CORS yahan import karna behtar hai
from app.api.chat import router as chat_router
from app.rag.ingest import ingest_data
from app.db.postgres import create_db_and_tables, engine
import asyncio

# Create a FastAPI app instance
app = FastAPI(
    title="RAG Chatbot Backend",
    description="A production-ready RAG chatbot backend using FastAPI and Gemini.",
    version="1.0.0",
)

# CORS Middleware Setup
origins = [
    "http://localhost:3000",  # Standard React/Docusaurus port
    "http://localhost:3001",  # AAPKA port jo terminal mein dikh raha hai
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    print("Application starting up...")
    print("Initializing database...")
    await create_db_and_tables()
    print("Database initialized.")
    print("Startup complete.")

# Include the chat router
app.include_router(chat_router, prefix="/api", tags=["Chat"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the RAG Chatbot API!"}