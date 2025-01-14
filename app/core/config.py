from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Portfolio AI"
    API_V1_STR: str = "/api/v1"
    
    MODEL_PATH: str = "models/mistral-7b-instruct.gguf"
    MODEL_URL: str = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    
    DATABASE_URL: str = "sqlite:///./portfolio.db"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 