from sqlmodel import SQLModel, create_engine, Session
from app.config import settings
import logging

def get_engine():
    db_url = settings.DATABASE_URL
    if db_url.startswith("mysql"):
        try:
            test_engine = create_engine(db_url, echo=False)
            with test_engine.connect() as conn:
                pass
            return test_engine
        except Exception as e:
            logging.warning(f"MySQL connection failed ({e}). Falling back to SQLite local database.")
            return create_engine("sqlite:///./ai_factory.db", echo=True, connect_args={"check_same_thread": False})
    
    connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}
    return create_engine(db_url, echo=True, connect_args=connect_args)

engine = get_engine()

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session