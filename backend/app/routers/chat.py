import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.dto import ChatRequest, ChatResponse
from app.services.chat import process_chat

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Process a natural language query about credit card spending."""
    logger.info(f"Chat query: {request.message[:100]}")
    result = process_chat(db, request.message)
    return ChatResponse(**result)
