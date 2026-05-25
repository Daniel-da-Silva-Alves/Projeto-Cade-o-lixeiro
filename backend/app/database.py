"""
Cadê o Lixeiro? v2.0 — Database Engine

Engine assíncrono SQLAlchemy com session maker para PostgreSQL (Supabase).
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# Engine async com pool de conexões
# statement_cache_size=0 é necessário para o Supabase Pooler (Supavisor/PgBouncer)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=1800,  # Reciclar conexões a cada 30 min
    connect_args={
        "statement_cache_size": 0,
    },
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Alias para uso em contextos fora do FastAPI Depends (ex: WebSockets)
async_session_factory = async_session


class Base(DeclarativeBase):
    """Base declarativa para todos os models SQLAlchemy."""
    pass


async def get_db():
    """Dependency que fornece uma sessão de banco por request."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
