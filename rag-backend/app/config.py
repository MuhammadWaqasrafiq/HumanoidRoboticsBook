import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Yeh line pakka karegi ke .env file load ho jaye chahe aap kisi bhi folder se command chalayein
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    DATABASE_URL: str
    QDRANT_URL: str
    QDRANT_API_KEY: str
    
    EMBEDDING_MODEL: str = "models/embedding-001"
    CHAT_MODEL: str = "gemini-1.5-flash"
    COLLECTION_NAME: str = "physical_book_rag"

    # Pydantic V2 syntax (recommended)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        # Agar ab bhi error aaye toh yeh debug info dikhayega
        print("--- DEBUG INFO ---")
        print(f"Error: {e}")
        print(f"Current Directory: {os.getcwd()}")
        print(f"Looking for .env in: {os.path.dirname(os.path.dirname(__file__))}")
        raise e

settings = get_settings()