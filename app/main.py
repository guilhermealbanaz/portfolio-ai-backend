from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.services.model_downloader import ModelDownloader
from app.models.database import init_db
from app.api.routes import router as api_router

app = FastAPI(title="Portfolio AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando aplicação...")
    
    init_db()
    logger.info("Banco de dados inicializado")
    
    downloader = ModelDownloader()
    if not downloader.download_model():
        logger.error("Falha ao baixar o modelo. A aplicação pode não funcionar corretamente.")

@app.get("/")
async def root():
    return {"message": "Portfolio AI Backend está funcionando!"} 