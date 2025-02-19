# Portfolio AI Backend

Backend do sistema de portfólio inteligente usando FastAPI e Mistral-7B LLM.

## 🛠️ Tecnologias

- Python 3.9+
- FastAPI
- SQLAlchemy
- Mistral-7B (LlamaCpp)
- SQLite

## 📋 Pré-requisitos

- Python 3.9 ou superior
- 16GB RAM (mínimo recomendado)
- pip e virtualenv

## 🚀 Instalação

1. Clone o repositório
2. cd portfolio-ai-backend
3. pip install -r requirements.txt
4. python -m venv venv
5. source venv/bin/activate
6. python main.py


## 📚 Documentação da API

Após iniciar o servidor, acesse:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 API Endpoints

### Currículo
- `POST /api/v1/resume/` - Adiciona uma nova entrada no currículo
- `GET /api/v1/resume/` - Lista todas as entradas do currículo
- `GET /api/v1/resume/?category=education` - Filtra entradas por categoria

### IA
- `POST /api/v1/ask/` - Faz uma pergunta sobre o currículo

## 🤖 Modelo LLM

O sistema usa o Mistral-7B-Instruct através do LlamaCpp. Na primeira execução, o modelo será baixado automaticamente.
