from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import get_conversations_by_user
from app.models import Conversation
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter()

class ConversationResponse(BaseModel):
    conversation_id: uuid.UUID
    created_at: datetime
    title: Optional[str] = None
    metadata: Optional[dict] = None

class UserChatsResponse(BaseModel):
    user_id: str
    page: int
    limit: int
    chats: List[ConversationResponse]

@router.get("/users/{user_id}/chats", response_model=UserChatsResponse)
async def get_user_chats_endpoint(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: AsyncSession = Depends(get_db)
):
    skip = (page - 1) * limit
    chats = await get_conversations_by_user(db, user_id, skip, limit)
    conversation_responses = [
        ConversationResponse(
            conversation_id=chat.conversation_id,
            created_at=chat.created_at,
            title=chat.title,
            metadata=chat.metadata
        )
        for chat in chats
    ]
    return {"user_id": user_id, "page": page, "limit": limit, "chats": conversation_responses}