import os
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings # Settings use karna behtar hai

# Base class for declarative models
Base = declarative_base()

# 1. Database URL Handling (Immutable Error Fix)
DATABASE_URL_STR = settings.DATABASE_URL

if not DATABASE_URL_STR:
    raise ValueError("DATABASE_URL environment variable is not set")

# URL parse karein
url_obj = make_url(DATABASE_URL_STR)

# Immutable dict se bachne ke liye query params ko naye dict mein copy karein
query_params = dict(url_obj.query)

# Agar sslmode hai toh usey remove karein taake asyncpg khush rahe
if "sslmode" in query_params:
    query_params.pop("sslmode")

# Naya URL object banayein with asyncpg driver and cleaned query
url_obj = url_obj.set(
    drivername="postgresql+asyncpg",
    query=query_params
)

# 2. Engine aur SSL Setup
# Neon/Cloud DBs ke liye SSL connect_args mein dena zaroori hai
connect_args = {}
if "neon.tech" in str(url_obj):
    connect_args = {"ssl": "require"}

engine = create_async_engine(
    url_obj,
    connect_args=connect_args,
    echo=False
)

# 3. Session aur Models
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# 4. Functions
async def create_db_and_tables():
    """Creates the database and all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully.")

async def get_db():
    """Dependency function to get an async database session."""
    async with AsyncSessionLocal() as session:
        yield session

if __name__ == "__main__":
    import asyncio
    print("Creating database and tables...")
    asyncio.run(create_db_and_tables())