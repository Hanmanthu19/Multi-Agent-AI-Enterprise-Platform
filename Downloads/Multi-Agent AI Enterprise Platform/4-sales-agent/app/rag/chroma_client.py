import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from app.logger import logger

class ChromaManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaManager, cls).__new__(cls)
            try:
                cls._instance.client = chromadb.PersistentClient(
                    path=settings.CHROMA_DB_DIR,
                    settings=ChromaSettings(allow_reset=True, anonymized_telemetry=False)
                )
                cls._instance.collection = cls._instance.client.get_or_create_collection(
                    name="enterprise_sales_docs"
                )
                logger.info(f"ChromaDB persistent store loaded at {settings.CHROMA_DB_DIR}")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {str(e)}")
                raise e
        return cls._instance

chroma_manager = ChromaManager()