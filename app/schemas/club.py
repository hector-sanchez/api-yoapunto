from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Club schemas
class ClubBase(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50, description="Club nickname (1-50 characters)")
    creator: str = Field(..., min_length=1, max_length=50, description="Club creator name (1-50 characters)")
    thumbnail_url: Optional[str] = Field(None, description="URL to club thumbnail image")

class ClubCreate(ClubBase):
    pass

class ClubUpdate(BaseModel):
    nickname: Optional[str] = Field(None, min_length=1, max_length=50, description="Club nickname (1-50 characters)")
    creator: Optional[str] = Field(None, min_length=1, max_length=50, description="Club creator name (1-50 characters)")
    thumbnail_url: Optional[str] = Field(None, description="URL to club thumbnail image")
    active: Optional[bool] = Field(None, description="Whether the club is active")

class Club(ClubBase):
    id: int
    active: bool = True  # Show default value in response
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
