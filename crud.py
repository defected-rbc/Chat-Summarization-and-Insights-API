from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from .models import Conversation, Message, Summary, Insight
from typing import List, Optional
import uuid

# Conversation CRUD Operations
async def create_conversation(db: AsyncSession, title: Optional[str] = None, metadata: Optional[dict] = None) -> Conversation:
    new_conversation = Conversation(title=title, metadata=metadata)
    db.add(new_conversation)
    await db.commit()
    await db.refresh(new_conversation)
    return new_conversation

async def get_conversation_by_id(db: AsyncSession, conversation_id: uuid.UUID) -> Optional[Conversation]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.conversation_id == conversation_id)
        .options(joinedload(Conversation.messages))
        .options(joinedload(Conversation.summary))
        .options(joinedload(Conversation.insights))
    )
    return result.scalar_one_or_none()

async def get_conversations_by_user(db: AsyncSession, user_id: str, skip: int = 0, limit: int = 10) -> List[Conversation]:
    # This assumes you might store user_id in the conversation metadata or messages
    # Adjust the query based on where you store user information relevant to a conversation.
    # The example below checks if the user_id exists in any of the messages within the conversation.
    result = await db.execute(
        select(Conversation)
        .join(Message)
        .where(Message.user_id == user_id)
        .order_by(Conversation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .distinct(Conversation.conversation_id) # Ensure unique conversations
    )
    return result.scalars().all()

async def delete_conversation(db: AsyncSession, conversation_id: uuid.UUID) -> Optional[dict]:
    conversation = await db.execute(
        select(Conversation).where(Conversation.conversation_id == conversation_id)
    )
    conversation = conversation.scalar_one_or_none()
    if conversation:
        await db.delete(conversation)
        await db.commit()
        return {"message": f"Conversation {conversation_id} deleted successfully"}
    return None

# Message CRUD Operations
async def create_message(db: AsyncSession, conversation_id: uuid.UUID, user_id: str, sender_type: str, content: str, metadata: Optional[dict] = None) -> Message:
    new_message = Message(conversation_id=conversation_id, user_id=user_id, sender_type=sender_type, content=content, metadata=metadata)
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message

async def get_conversation_messages(db: AsyncSession, conversation_id: uuid.UUID, skip: int = 0, limit: int = 10) -> List[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp.asc()) # Showing messages in chronological order
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

# Summary CRUD Operations
async def create_summary(db: AsyncSession, conversation_id: uuid.UUID, summary_text: str, model_used: Optional[str] = None, metadata: Optional[dict] = None) -> Summary:
    new_summary = Summary(conversation_id=conversation_id, summary_text=summary_text, model_used=model_used, metadata=metadata)
    db.add(new_summary)
    try:
        await db.commit()
        await db.refresh(new_summary)
        return new_summary
    except Exception as e:
        await db.rollback()
        raise e

async def get_summary_by_conversation_id(db: AsyncSession, conversation_id: uuid.UUID) -> Optional[Summary]:
    result = await db.execute(
        select(Summary).where(Summary.conversation_id == conversation_id)
    )
    return result.scalar_one_or_none()

# Insight CRUD Operations
async def create_insight(db: AsyncSession, conversation_id: uuid.UUID, insight_type: str, insight_data: dict, model_used: Optional[str] = None, metadata: Optional[dict] = None) -> Insight:
    new_insight = Insight(conversation_id=conversation_id, insight_type=insight_type, insight_data=insight_data, model_used=model_used, metadata=metadata)
    db.add(new_insight)
    await db.commit()
    await db.refresh(new_insight)
    return new_insight

async def get_insights_by_conversation_id_and_type(db: AsyncSession, conversation_id: uuid.UUID, insight_type: str) -> List[Insight]:
    result = await db.execute(
        select(Insight)
        .where(Insight.conversation_id == conversation_id)
        .where(Insight.insight_type == insight_type)
    )
    return result.scalars().all()