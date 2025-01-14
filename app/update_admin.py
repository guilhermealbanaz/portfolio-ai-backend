from app.database import SessionLocal
from app.models.database import User
from loguru import logger

def make_user_admin(username: str = 'admin'):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.is_admin = True
            db.commit()
            logger.info(f"Usuário agora é admin")
        else:
            logger.error(f"Usuário não encontrado")
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    make_user_admin("admin") 