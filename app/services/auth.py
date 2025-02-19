from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from app.models.database import User
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.database import get_db
from app.schemas.auth import TokenData
from loguru import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "seu_secret_key_seguro"  # Mova isto para config.py em produção
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user 

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Função para obter o usuário atual baseado no token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.debug(f"Decodificando token...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        logger.debug(f"Username do token: {username}")
        
        if username is None:
            logger.error("Username não encontrado no token")
            raise credentials_exception
            
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            logger.error(f"Usuário {username} não encontrado no banco")
            raise credentials_exception
            
        logger.debug(f"Usuário encontrado: {user.username}, is_admin: {user.is_admin}")
        return user
        
    except JWTError as e:
        logger.error(f"Erro ao decodificar token: {str(e)}")
        raise credentials_exception

async def get_current_active_admin(
    current_user: User = Depends(get_current_user)
):
    """
    Função para verificar se o usuário atual é admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O usuário não tem permissões de administrador"
        )
    return current_user 