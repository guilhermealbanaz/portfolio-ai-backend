from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.models.database import SessionLocal, User
from app.services.database import create_resume_entry, get_resume_entries
from app.services.llm import LLMService
from loguru import logger
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_password_hash
)
from app.schemas.auth import Token, UserCreate, User as UserSchema
from app.schemas.resume import ResumeEntryCreate, ResumeEntry

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
def list_resume_entries(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todas as entradas do currículo"""
    try:
        return get_resume_entries(db, category)
    except Exception as e:
        logger.error(f"Erro ao listar entradas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar entradas: {str(e)}"
        )

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

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Rota de login que retorna um token JWT"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    } 

@router.post("/protected/resume", response_model=ResumeEntry)
async def protected_add_resume_entry(
    entry: ResumeEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adiciona uma nova entrada no currículo (requer autenticação)"""
    try:
        # Verifica se o usuário é admin
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem adicionar entradas"
            )
        
        return create_resume_entry(
            db=db,
            category=entry.category,
            title=entry.title,
            description=entry.description,
            start_date=entry.start_date,
            end_date=entry.end_date
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar entrada: {str(e)}"
        )

@router.post("/users", response_model=UserSchema)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Cria um novo usuário"""
    try:
        # Verifica se o usuário já existe
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já registrado"
            )
        
        # Cria o novo usuário
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            password_hash=hashed_password,
            is_admin=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar usuário: {str(e)}"
        )