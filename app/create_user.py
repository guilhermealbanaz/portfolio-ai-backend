from app.database import SessionLocal
from app.models.database import User
from app.services.auth import get_password_hash
from loguru import logger

def create_admin_user(username: str, password: str):
    db = SessionLocal()
    try:
        # Verifica se o usuário já existe
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            logger.info(f"Usuário {username} já existe. Atualizando para admin...")
            existing_user.is_admin = True
            db.commit()
            db.refresh(existing_user)
            logger.info(f"Usuário atualizado: {existing_user.username}, is_admin: {existing_user.is_admin}")
            return
        
        # Cria novo usuário admin
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            password_hash=hashed_password,
            is_admin=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"Novo usuário admin criado: {new_user.username}, is_admin: {new_user.is_admin}")
        
    except Exception as e:
        logger.error(f"Erro ao criar/atualizar usuário: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Cria um novo usuário admin1
    create_admin_user("admin1", "senha1234") 