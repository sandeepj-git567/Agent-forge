"""
Database Session and Engine Management for AgentForge AI
"""
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from agentforge.config.settings import settings
from agentforge.db.base import Base

DATABASE_URL = settings.DATABASE_URL or "sqlite:///:memory:"

# Connection pool & args configuration based on database dialect
connect_args: dict[str, Any] = {}
engine_kwargs: dict[str, Any] = {
    "pool_pre_ping": True,
}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # PostgreSQL connection pooling defaults
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800,
    })

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency for providing database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for standalone database operations with auto-rollback on error."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_database_health() -> dict[str, Any]:
    """
    Check database connection health, latency, dialect, and pgvector extension.
    Never exposes passwords or sensitive credentials.
    """
    start_time = time.time()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            latency_ms = round((time.time() - start_time) * 1000, 2)
            dialect = engine.dialect.name
            
            # Check pgvector extension status if PostgreSQL
            has_pgvector = False
            if dialect == "postgresql":
                try:
                    res = conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")).fetchone()
                    has_pgvector = res is not None
                except Exception:
                    has_pgvector = False
                    
            return {
                "status": "healthy",
                "dialect": dialect,
                "latency_ms": latency_ms,
                "is_postgresql": dialect == "postgresql",
                "pgvector_enabled": has_pgvector,
            }
    except Exception as err:
        return {
            "status": "unhealthy",
            "dialect": engine.dialect.name if hasattr(engine, "dialect") else "unknown",
            "error": "Failed to connect to database.",
            "is_postgresql": False,
            "pgvector_enabled": False,
        }

