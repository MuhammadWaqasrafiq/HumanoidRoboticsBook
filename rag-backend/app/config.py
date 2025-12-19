import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings.
    - GOOGLE_API_KEY: Your Google API key for Gemini.
    - QDRANT_HOST: The host for the Qdrant vector database.
    - QDRANT_PORT: The port for the Qdrant vector database.
    - EMBEDDING_MODEL: The model to use for generating embeddings.
    - CHAT_MODEL: The model to use for chat generation.
    - COLLECTION_NAME: The name of the Qdrant collection.
    """
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    
    EMBEDDING_MODEL: str = "models/embedding-001"
    CHAT_MODEL: str = "gemini-1.5-flash"
    
    COLLECTION_NAME: str = "physical_book_rag"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings() -> Settings:
    """Returns the settings instance."""
    return Settings()

settings = get_settings()
