# RAG Chatbot Backend with FastAPI and Gemini

This project is a complete, production-ready, and free RAG (Retrieval-Augmented Generation) chatbot backend built with Python and FastAPI. It uses the free Google Gemini API for embeddings and chat generation, and a local Qdrant instance for the vector store.

This backend is designed to answer questions based *only* on the content of a provided text file (`data/book.txt`).

## Project Structure

```
rag-backend/
 ├── app/
 │   ├── main.py          # FastAPI app entrypoint
 │   ├── config.py        # Application configuration
 │   ├── api/chat.py      # /chat API endpoint
 │   ├── rag/
 │   │   ├── embeddings.py  # Gemini embedding generation
 │   │   ├── retriever.py   # Qdrant vector retrieval
 │   │   ├── agent.py       # Core RAG agent logic
 │   │   └── ingest.py      # Data ingestion script
 │   └── db/
 │       └── sqlite.py      # SQLite database setup (for chat history, etc.)
 ├── data/
 │   └── book.txt         # The source document for the RAG chatbot
 ├── requirements.txt
 ├── .env.example
 └── README.md
```

## Features

- **FastAPI Backend**: A robust and modern API framework.
- **Gemini Free Tier**: Uses `gemini-1.5-flash` for chat and `embedding-001` for embeddings, requiring only a free Google AI Studio API key.
- **Local Vector Store**: Uses Qdrant in-memory for simplicity, with no need for Docker or a separate server.
- **Strictly Contextual Answers**: The chatbot is explicitly prompted to answer **only** from the book's content or respond with `"Not found in the book."
- **Modular Code**: The codebase is organized into logical modules for easy understanding and extension.

## Getting Started

Follow these steps to set up and run the project locally.

### 1. Prerequisites

- Python 3.9+
- A Google AI Studio API Key. You can get one for free from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Clone the Repository

Clone this project to your local machine.

### 3. Set Up a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
# Navigate into the project directory
cd rag-backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

Install all the required Python packages.

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file by copying the example file.

```bash
# On Windows
copy .env.example .env
# On macOS/Linux
cp .env.example .env
```

Now, open the `.env` file and replace `"YOUR_GOOGLE_API_KEY"` with your actual Google API key.

```env
# .env
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
```

### 6. Run the Application

Launch the FastAPI server using `uvicorn`.

```bash
uvicorn app.main:app --reload
```

The `--reload` flag automatically restarts the server when you make code changes.

The server will start, and you will see output indicating that the data ingestion process is running. This happens only on startup.

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using statreload
INFO:     Started server process [12347]
INFO:     Waiting for application startup.
Application starting up...
Initializing database...
Database initialized.
Ingesting data into vector store...
Starting data ingestion...
Loading data from rag-backend/data/book.txt...
Chunking text...
Created 5 chunks.
Initializing embedding and retriever clients...
Upserting documents into Qdrant...
Data ingestion completed successfully!
Data ingestion complete.
Startup complete.
INFO:     Application startup complete.
```

## API Usage

You can interact with the chatbot by sending a `POST` request to the `/api/chat` endpoint.

### Example Request

Here is an example using `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
-H "Content-Type: application/json" \
-d '{"message": "What is the AI winter?"}'
```

### Example Success Response

If the answer is found in the book, you will get a response like this:

```json
{
  "answer": "The 'first AI winter' was a period in the mid-1970s when progress in AI slowed down due to unmet promises and computational limitations, leading to a significant reduction in funding and interest."
}
```

### Example "Not Found" Response

If the answer cannot be found in the context of the book, you will get this specific response:

```bash
# Request for information not in the book
curl -X POST "http://127.0.0.1:8000/api/chat" \
-H "Content-Type: application/json" \
-d '{"message": "What is the capital of France?"}'
```

```json
{
  "answer": "Not found in the book."
}
```

You can also access the interactive API documentation provided by FastAPI at `http://127.0.0.1:8000/docs`.

```