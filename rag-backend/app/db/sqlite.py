from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime
import os

# Define the database file path
DB_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'db')
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'chat_history.db')}"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Needed for SQLite with FastAPI
)

# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Example Model: ChatHistory
class ChatHistory(Base):
    """
    A model to store chat history.
    This is an example and can be extended as needed.
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

def create_db_and_tables():
    """
    Creates the database and all tables defined in the Base metadata.
    """
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    A dependency function to get a database session.
    It ensures the database session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# You can run this file directly to create the initial database and table
if __name__ == "__main__":
    print("Creating database and tables...")
    create_db_and_tables()
    print("Database and tables created successfully.")
