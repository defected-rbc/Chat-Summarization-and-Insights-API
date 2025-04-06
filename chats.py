from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import (
    create_message,
    get_conversation_by_id,
    delete_conversation,
    create_summary,
    get_conversation_messages,
    create_insight,
    get_insights_by_conversation_id_and_type,
)
from app.models import Message, Conversation, Summary, Insight  # Updated model imports
from pydantic import BaseModel
import openai
import os
from typing import List, Optional
import uuid
from datetime import datetime
from sqlalchemy.future import select

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter()

# Pydantic models for request validation (existing ones)
class ChatCreateRequest(BaseModel):
    conversation_id: uuid.UUID
    user_id: str
    sender_type: str
    content: str
    metadata: Optional[dict] = None

class SummarizeRequest(BaseModel):
    conversation_id: uuid.UUID

class ConversationResponse(BaseModel):
    conversation_id: uuid.UUID
    created_at: datetime
    title: Optional[str] = None
    metadata: Optional[dict] = None
    messages: List["MessageResponse"] = []
    summary: Optional["SummaryResponse"] = None
    insights: List["InsightResponse"] = [] # Add insights to the response

class MessageResponse(BaseModel):
    message_id: int
    user_id: str
    sender_type: str
    content: str
    timestamp: datetime
    metadata: Optional[dict] = None

class SummaryResponse(BaseModel):
    summary_id: int
    summary_text: str
    created_at: datetime
    model_used: Optional[str] = None
    metadata: Optional[dict] = None

class InsightResponse(BaseModel):
    insight_id: int
    insight_type: str
    insight_data: dict
    created_at: datetime
    model_used: Optional[str] = None
    metadata: Optional[dict] = None

ConversationResponse.update_forward_refs()

@router.post("/chats", response_model=MessageResponse)
async def add_chat(request: ChatCreateRequest, db: AsyncSession = Depends(get_db)):
    message = await create_message(db, request.conversation_id, request.user_id, request.sender_type, request.content, request.metadata)
    return message

@router.get("/chats/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = await get_conversation_messages(db, conversation_id=conversation_id)
    summary = await db.execute(select(Summary).where(Summary.conversation_id == conversation_id))
    summary = summary.scalar_one_or_none()
    insights = await get_insights_by_conversation_id_and_type(db, conversation_id=conversation_id) # Get all insights for now
    return ConversationResponse(
        conversation_id=conversation.conversation_id,
        created_at=conversation.created_at,
        title=conversation.title,
        metadata=conversation.metadata,
        messages=[MessageResponse(**msg.__dict__) for msg in messages],
        summary=SummaryResponse(**summary.__dict__) if summary else None,
        insights=[InsightResponse(**insight.__dict__) for insight in insights]
    )

@router.post("/chats/summarize", response_model=SummaryResponse)
async def summarize_chat(request: SummarizeRequest, db: AsyncSession = Depends(get_db)):
    conversation = await get_conversation_by_id(db, request.conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await get_conversation_messages(db, conversation_id=request.conversation_id)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found in this conversation to summarize.")

    conversation_text = "\n".join([f"{msg.sender_type} ({msg.user_id}): {msg.content}" for msg in messages])

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following conversation:"},
                {"role": "user", "content": conversation_text},
            ]
        )
        summary_text = response.choices[0].message['content']
        summary = await create_summary(db, conversation_id=request.conversation_id, summary_text=summary_text, model_used="gpt-3.5-turbo")
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")

@router.delete("/chats/{conversation_id}")
async def delete_conversation_endpoint(conversation_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await delete_conversation(db, conversation_id)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result

@router.post("/chats/{conversation_id}/insights")
async def generate_conversation_insights(conversation_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await get_conversation_messages(db, conversation_id=conversation_id)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found in this conversation to analyze for insights.")

    conversation_text = "\n".join([f"{msg.sender_type} ({msg.user_id}): {msg.content}" for msg in messages])
    insights_data = []

    # Sentiment Analysis
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Analyze the sentiment of the following conversation. Provide the overall sentiment as 'positive', 'negative', or 'neutral' and a brief explanation."},
                {"role": "user", "content": conversation_text},
            ]
        )
        sentiment_result = response.choices[0].message['content']
        await create_insight(db, conversation_id=conversation_id, insight_type="sentiment", insight_data={"result": sentiment_result}, model_used="gpt-3.5-turbo")
        insights_data.append({"type": "sentiment", "result": sentiment_result})
    except Exception as e:
        print(f"Error during sentiment analysis: {e}")

    # Keyword Extraction
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Extract the top 5 most important keywords or topics from the following conversation. Provide them as a comma-separated list."},
                {"role": "user", "content": conversation_text},
            ]
        )
        keywords_result = response.choices[0].message['content']
        keywords_list = [keyword.strip() for keyword in keywords_result.split(',')]
        await create_insight(db, conversation_id=conversation_id, insight_type="keywords", insight_data={"keywords": keywords_list}, model_used="gpt-3.5-turbo")
        insights_data.append({"type": "keywords", "keywords": keywords_list})
    except Exception as e:
        print(f"Error during keyword extraction: {e}")

    return {"conversation_id": conversation_id, "insights": insights_data}