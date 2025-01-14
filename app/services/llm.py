from llama_cpp import Llama
from pathlib import Path
from loguru import logger
from typing import List, Optional, Dict
from app.core.config import settings
from app.models.database import ResumeEntry
from functools import lru_cache
import threading

class LLMService:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implementa Singleton pattern para garantir uma única instância do modelo"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.model_path = Path(settings.MODEL_PATH)
            self.model = None
            self.context_size = 4096
            self.max_tokens = 512
            self.temperature = 0.7
            self.cache_size = 100
            self.initialized = True
            self.initialize_model()

    def initialize_model(self):
        """Inicializa o modelo LLM com configurações mais conservadoras"""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Modelo não encontrado em {self.model_path}")
            
            self.model = Llama(
                model_path=str(self.model_path),
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=0,
                n_batch=8,
                embedding=False
            )
            logger.info("Modelo LLM inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar o modelo: {str(e)}")
            raise

    @lru_cache(maxsize=100)
    def get_cached_response(self, question: str, context_hash: str) -> Optional[str]:
        """Cache de respostas para perguntas similares"""
        return None

    def prepare_context(self, resume_entries: List[ResumeEntry]) -> str:
        """Prepara o contexto do currículo com otimização de tokens"""
        sections = {
            "education": "FORMAÇÃO ACADÊMICA",
            "experience": "EXPERIÊNCIA PROFISSIONAL",
            "skills": "HABILIDADES",
            "projects": "PROJETOS"
        }
        
        context_parts = []
        entries_by_category = self._group_entries(resume_entries)
        
        for category, entries in entries_by_category.items():
            if entries:
                section_title = sections.get(category, category.upper())
                context_parts.append(f"\n{section_title}:")
                
                for entry in entries:
                    context_parts.extend(self._format_entry(entry))
        
        return "\n".join(context_parts)

    def _group_entries(self, entries: List[ResumeEntry]) -> Dict[str, List[ResumeEntry]]:
        """Agrupa entradas por categoria de forma eficiente"""
        grouped = {}
        for entry in entries:
            if entry.category not in grouped:
                grouped[entry.category] = []
            grouped[entry.category].append(entry)
        return grouped

    def _format_entry(self, entry: ResumeEntry) -> List[str]:
        """Formata uma entrada individual do currículo"""
        parts = [f"- {entry.title}"]
        if entry.description:
            parts.append(f"  {entry.description}")
        if entry.start_date and entry.end_date:
            date_str = f"  Período: {entry.start_date.strftime('%Y-%m')} até {entry.end_date.strftime('%Y-%m')}"
            parts.append(date_str)
        return parts

    def generate_response(self, question: str, context: str) -> str:
        """Gera uma resposta com configurações mais básicas"""
        try:
            prompt = f"""Pergunta: {question}

Contexto:
{context}

Resposta:"""

            logger.info(f"Gerando resposta para prompt: {prompt}")

            response = self.model(
                prompt,
                max_tokens=256,
                temperature=0.5,
                top_p=0.95,
                top_k=40,
                repeat_penalty=1.0,
                echo=False
            )

            logger.info(f"Resposta bruta do modelo: {response}")

            if not response or 'choices' not in response:
                logger.error("Formato de resposta inválido")
                return "Erro ao gerar resposta."

            text = response['choices'][0]['text'].strip()
            logger.info(f"Texto extraído: {text}")

            return text if text else "Não foi possível gerar uma resposta."

        except Exception as e:
            logger.error(f"Erro detalhado na geração: {str(e)}")
            return f"Erro ao processar: {str(e)}"

    def answer_question(self, question: str, resume_entries: List[ResumeEntry]) -> str:
        """Método principal otimizado para responder perguntas"""
        try:
            logger.info(f"Processando pergunta: {question}")
            
            context = self.prepare_context(resume_entries)
            context_hash = str(hash(context))
            
            cached_response = self.get_cached_response(question, context_hash)
            if cached_response:
                logger.info("Resposta encontrada no cache")
                return cached_response
            
            response = self.generate_response(question, context)
            logger.info("Nova resposta gerada com sucesso")
            
            return response
            
        except Exception as e:
            logger.error(f"Erro em answer_question: {str(e)}")
            return "Ocorreu um erro ao processar sua pergunta." 