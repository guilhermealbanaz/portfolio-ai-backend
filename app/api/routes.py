from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.database import SessionLocal
from app.services.database import create_resume_entry, get_resume_entries
from app.services.llm import LLMService
from loguru import logger

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

llm_service = LLMService()

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

class QuestionRequest(BaseModel):
    question: str

@router.post("/resume/", response_model=ResumeEntry)
def add_resume_entry(entry: ResumeEntryCreate, db: Session = Depends(get_db)):
    """Adiciona uma nova entrada no currículo"""
    return create_resume_entry(
        db=db,
        category=entry.category,
        title=entry.title,
        description=entry.description,
        start_date=entry.start_date,
        end_date=entry.end_date
    )

@router.get("/resume/", response_model=List[ResumeEntry])
def list_resume_entries(category: Optional[str] = None, db: Session = Depends(get_db)):
    """Lista todas as entradas do currículo, opcionalmente filtradas por categoria"""
    return get_resume_entries(db, category)

@router.post("/ask/")
def ask_question(question_req: QuestionRequest, db: Session = Depends(get_db)):
    """Responde a uma pergunta sobre o currículo usando o LLM"""
    try:
        resume_entries = get_resume_entries(db)
        
        response = llm_service.answer_question(question_req.question, resume_entries)
        
        return {
            "question": question_req.question,
            "answer": response
        }
    except Exception as e:
        logger.error(f"Erro ao processar pergunta: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar sua pergunta"
        ) 