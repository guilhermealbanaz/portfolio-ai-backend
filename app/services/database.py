from sqlalchemy.orm import Session
from app.models.database import ResumeEntry
from datetime import datetime
from typing import List, Optional
from loguru import logger

def create_resume_entry(
    db: Session,
    category: str,
    title: str,
    description: str,
    start_date: datetime = None,
    end_date: datetime = None
) -> ResumeEntry:
    """Cria uma nova entrada no currículo"""
    try:
        logger.debug(f"Criando entrada: categoria={category}, título={title}")
        
        # Converte a data se for string
        if isinstance(start_date, str):
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError as e:
                logger.error(f"Erro ao converter data: {e}")
                raise ValueError(f"Formato de data inválido: {e}")

        # Cria a entrada
        db_entry = ResumeEntry(
            category=category,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Adiciona e commita
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        logger.debug(f"Entrada criada com sucesso: ID={db_entry.id}")
        return db_entry
        
    except Exception as e:
        logger.error(f"Erro ao criar entrada no banco: {str(e)}")
        db.rollback()
        raise 

def get_resume_entries(db: Session, category: Optional[str] = None) -> List[ResumeEntry]:
    """Retorna todas as entradas do currículo, opcionalmente filtradas por categoria"""
    try:
        query = db.query(ResumeEntry)
        if category:
            query = query.filter(ResumeEntry.category == category)
        return query.all()
    except Exception as e:
        logger.error(f"Erro ao buscar entradas do currículo: {str(e)}")
        raise 