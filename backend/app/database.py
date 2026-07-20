# ============================================================
# app/database.py — Configuración de la base de datos async
# Motor: PostgreSQL + PostGIS con asyncpg
# ============================================================

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


# URL de conexión a PostgreSQL (configurable por variable de entorno)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://apuradito:apuradito2026@localhost:5432/apuradito_db",
)

# Motor async con pool de conexiones
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para ver SQL en consola (desarrollo)
    pool_pre_ping=True,  # Verificar conexión antes de usarla
    pool_size=10,
    max_overflow=20,
)

# Fábrica de sesiones async
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos SQLAlchemy."""

    pass


async def get_db() -> AsyncSession:
    """
    Dependencia de FastAPI para obtener sesión de base de datos.
    Uso: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def crear_tablas():
    """Crea todas las tablas en la base de datos (solo para desarrollo/tests)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
