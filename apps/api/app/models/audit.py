from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    user_role = Column(String(50), nullable=True)
    branch_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    language = Column(String(10), default="en")
    user_question = Column(Text, nullable=False)
    conversation_id = Column(String(100), nullable=True, index=True)
    ai_provider = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    generated_sql = Column(Text, nullable=True)
    validated_sql = Column(Text, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    result_row_count = Column(Integer, nullable=True)
    chart_type = Column(String(50), nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    final_response = Column(Text, nullable=True)
    token_count = Column(Integer, nullable=True)
