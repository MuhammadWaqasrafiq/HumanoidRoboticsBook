from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.rag.agent import RAGAgent, get_rag_agent
from app.db.postgres import get_db, ChatHistory
import uuid

router = APIRouter()

class ChatRequest(BaseModel):
    """
    Request model for the chat endpoint.
    """
    message: str
    session_id: str | None = None
    context: str | None = None

class ChatResponse(BaseModel):
    """
    Response model for the chat endpoint.
    """
    answer: str
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def handle_chat(
    request: ChatRequest,
    rag_agent: RAGAgent = Depends(get_rag_agent),
    db: AsyncSession = Depends(get_db)
):
    """
    Handles a chat request, generates an answer, and saves the chat history.
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        answer = await rag_agent.generate_answer(request.message, context=request.context)
        
        # Save chat history
        chat_record = ChatHistory(
            session_id=session_id,
            user_message=request.message,
            bot_response=answer
        )
        db.add(chat_record)
        await db.commit()
        
        return ChatResponse(answer=answer, session_id=session_id)
    except Exception as e:
        print(f"An error occurred in the chat endpoint: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="An internal error occurred.")
