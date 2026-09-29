from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from app.core.database import Base

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    role = Column(String(50), nullable=False)  # User role at the time (e.g. "Admin", "Branch Manager")
    user_message = Column(Text, nullable=False)
    assistant_response = Column(Text, nullable=False)
    detected_intent = Column(String(50), nullable=False)  # GENERAL_CONVERSATION, ERP_ANALYTICS, CONTEXTUAL
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    audit_reference = Column(Integer, nullable=True)  # References AuditLog.id if ERP analytics was run

    __table_args__ = (
        Index("idx_conversation_user", "conversation_id", "user_id"),
    )
