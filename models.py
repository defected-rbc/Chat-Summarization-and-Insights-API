from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID, BIGINT
from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    title = Column(Text)
    conversation_metadata = Column(JSON)  # Renamed metadata

    messages = relationship("Message", back_populates="conversation")
    summary = relationship("Summary", back_populates="conversation", uselist=False)
    insights = relationship("Insight", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(BIGINT, primary_key=True, autoincrement=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.conversation_id"), nullable=False)
    user_id = Column(Text, nullable=False)
    sender_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    msg_metadata = Column(JSON)  # Renamed metadata

    conversation = relationship("Conversation", back_populates="messages")

class Summary(Base):
    __tablename__ = "summaries"

    summary_id = Column(BIGINT, primary_key=True, autoincrement=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.conversation_id"), nullable=False, unique=True)
    summary_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    model_used = Column(String(255))
    summary_metadata = Column(JSON)  # Renamed metadata

    conversation = relationship("Conversation", back_populates="summary")

class Insight(Base):
    __tablename__ = "insights"

    insight_id = Column(BIGINT, primary_key=True, autoincrement=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.conversation_id"), nullable=False)
    insight_type = Column(String(100), nullable=False)
    insight_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    model_used = Column(String(255))
    insight_metadata = Column(JSON)  # Renamed metadata

    conversation = relationship("Conversation", back_populates="insights")

# Example Pydantic Models (You might need to update these if you were using the 'metadata' field)
class ChatMessageCreate(BaseModel):
    user_id: str
    sender_type: str
    content: str
    metadata: Optional[dict] = None  # Keep as 'metadata' for API request/response

class ConversationRead(BaseModel):
    conversation_id: uuid.UUID
    created_at: datetime
    title: Optional[str] = None
    metadata: Optional[dict] = None  # Keep as 'metadata' for API request/response
    messages: List["MessageRead"] = []
    summary: Optional["SummaryRead"] = None
    insights: List["InsightRead"] = []

class MessageRead(BaseModel):
    message_id: int
    user_id: str
    sender_type: str
    content: str
    timestamp: datetime
    metadata: Optional[dict] = None  # Keep as 'metadata' for API request/response

class SummaryRead(BaseModel):
    summary_id: int
    summary_text: str
    created_at: datetime
    model_used: Optional[str] = None
    metadata: Optional[dict] = None  # Keep as 'metadata' for API request/response

class InsightRead(BaseModel):
    insight_id: int
    insight_type: str
    insight_data: dict
    created_at: datetime
    model_used: Optional[str] = None
    metadata: Optional[dict] = None  # Keep as 'metadata' for API request/response

# ForwardRef to handle circular dependencies in Pydantic models
ConversationRead.update_forward_refs()