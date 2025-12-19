from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.rag.agent import RAGAgent, get_rag_agent

router = APIRouter()

class ChatRequest(BaseModel):
    """
    Request model for the chat endpoint.
    """
    message: str

class ChatResponse(BaseModel):
    """
    Response model for the chat endpoint.
    """
    answer: str

@router.post("/chat", response_model=ChatResponse)
def handle_chat(
    request: ChatRequest,
    rag_agent: RAGAgent = Depends(get_rag_agent)
):
    """
    Handles a chat request and returns the RAG agent's answer.
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    try:
        answer = rag_agent.generate_answer(request.message)
        return ChatResponse(answer=answer)
    except Exception as e:
        print(f"An error occurred in the chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")
