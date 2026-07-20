"""Configuración de la base de datos con SQLAlchemy async."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from app.core.config import settings


# Motor de base de datos async
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

# Fábrica de sesiones
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Clase base para todos los modelos SQLAlchemy."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency de FastAPI para obtener sesión de BD."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Crear todas las tablas (usar solo en desarrollo)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
