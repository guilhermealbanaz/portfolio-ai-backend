from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.services.model_downloader import ModelDownloader
from app.models.database import init_db, Base
from app.api.routes import router
from app.database import create_tables, engine

app = FastAPI(title="Portfolio AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando aplicação...")
    
    init_db()
    logger.info("Banco de dados inicializado")
    
    downloader = ModelDownloader()
    if not downloader.download_model():
        logger.error("Falha ao baixar o modelo. A aplicação pode não funcionar corretamente.")

    # Criar tabelas ao iniciar a aplicação
    create_tables()

@app.get("/")
async def root():
    return {"message": "Portfolio AI Backend está funcionando!"} 

# Criar tabelas
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}") 