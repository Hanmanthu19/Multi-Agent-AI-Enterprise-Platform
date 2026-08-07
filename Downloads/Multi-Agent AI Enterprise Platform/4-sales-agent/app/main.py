from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.database import init_db
from app.api.routes import router as sales_router
from app.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing application resources...")
    init_db()
    yield
    logger.info("Application shutdown complete.")

app = FastAPI(
    title="Enterprise AI Sales Agent API",
    version="1.0.0",
    description="Production-Ready AI Sales Agent with LangGraph & Google Gemini API",
    lifespan=lifespan
)

app.include_router(sales_router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Enterprise AI Sales Agent",
        "model": settings.MODEL_NAME
    }