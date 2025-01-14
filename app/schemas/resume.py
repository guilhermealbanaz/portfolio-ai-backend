from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ResumeEntryBase(BaseModel):
    category: str
    title: str
    description: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ResumeEntryCreate(ResumeEntryBase):
    pass

class ResumeEntry(ResumeEntryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 