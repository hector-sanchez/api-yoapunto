from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(50), nullable=False, index=True)  # Max 50 chars, required
    creator = Column(String(50), nullable=False)  # Max 50 chars, required
    thumbnail_url = Column(String)  # URL or file path to the thumbnail image
    active = Column(Boolean, default=True, nullable=False)  # Defaults to True
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
