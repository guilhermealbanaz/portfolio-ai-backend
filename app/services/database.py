from sqlalchemy.orm import Session
from app.models.database import ResumeEntry
from datetime import datetime
from typing import List, Optional

def create_resume_entry(
    db: Session,
    category: str,
    title: str,
    description: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> ResumeEntry:
    db_entry = ResumeEntry(
        category=category,
        title=title,
        description=description,
        start_date=start_date,
        end_date=end_date
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def get_resume_entries(
    db: Session,
    category: Optional[str] = None
) -> List[ResumeEntry]:
    query = db.query(ResumeEntry)
    if category:
        query = query.filter(ResumeEntry.category == category)
    return query.all() 