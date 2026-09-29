from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    preferred_language = Column(String(10), default="en")  # "en" or "ar"
    preferred_response_style = Column(String(50), default="concise")  # "concise", "detailed", "executive"
    preferred_report_format = Column(String(50), default="table_and_chart")  # "table_and_chart", "chart_only", "table_only"
    terminology_preference = Column(String(50), default="standard")  # "standard", "formal", "technical"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="preferences", lazy="joined")
