import requests
from pathlib import Path
from tqdm import tqdm
import hashlib
from loguru import logger
from app.core.config import settings

class ModelDownloader:
    def __init__(self):
        self.model_path = Path(settings.MODEL_PATH)
        self.model_url = settings.MODEL_URL
        self.chunk_size = 8192

    def calculate_md5(self, file_path: Path) -> str:
        """Calcula o MD5 do arquivo para verificação"""
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def download_model(self) -> bool:
        """
        Faz o download do modelo se ele não existir localmente
        Retorna True se o download foi bem sucedido ou o arquivo já existe
        """
        try:
            if self.model_path.exists():
                logger.info(f"Modelo já existe em {self.model_path}")
                return True

            logger.info(f"Iniciando download do modelo de {self.model_url}")
            
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            
            response = requests.get(self.model_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(self.model_path, 'wb') as file, \
                 tqdm(
                    desc="Downloading",
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as progress_bar:
                
                for data in response.iter_content(chunk_size=self.chunk_size):
                    size = file.write(data)
                    progress_bar.update(size)
            
            logger.success(f"Download concluído: {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Erro ao baixar modelo: {str(e)}")
            if self.model_path.exists():
                self.model_path.unlink()
            return False 