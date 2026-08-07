import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    CHROMA_DB_DIR: str = "./data/chroma_db"
    DATA_DIR: str = "./app/data"
    DATABASE_URL: str = "sqlite:///./sales_agent.db"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure required runtime directories exist
Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.CHROMA_DB_DIR).mkdir(parents=True, exist_ok=True)