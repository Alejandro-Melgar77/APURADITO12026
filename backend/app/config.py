# ============================================================
# app/config.py — Configuración global de la aplicación
# Variables de entorno con valores por defecto
# ============================================================

from functools import lru_cache
from pydantic_settings import BaseSettings


class Configuracion(BaseSettings):
    """Configuración central de la aplicación Apuradito."""

    # --- App ---
    APP_NOMBRE: str = "Apuradito API"
    APP_VERSION: str = "1.0.0"
    APP_DEBUG: bool = False
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # --- Base de Datos ---
    DATABASE_URL: str = (
        "postgresql+asyncpg://apuradito:apuradito2026@localhost:5432/apuradito_db"
    )

    # --- JWT ---
    JWT_SECRET_KEY: str = "apuradito-super-secreto-2026-cambia-esto-en-produccion"
    JWT_ALGORITMO: str = "HS256"
    JWT_EXPIRE_MINUTOS: int = 60  # Access token: 1 hora
    JWT_REFRESH_EXPIRE_DIAS: int = 30  # Refresh token: 30 días

    # --- Seguridad ---
    BCRYPT_ROUNDS: int = 12
    CORS_ORIGINS: list[str] = ["*"]

    # --- Google Firebase (Fase 5) ---
    GOOGLE_CLIENT_ID: str = ""
    FIREBASE_CREDENTIALS_PATH: str = ""

    # --- Almacenamiento (Fase 3) ---
    STORAGE_BACKEND: str = "local"  # local | s3 | gcs
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def obtener_config() -> Configuracion:
    """Retorna instancia cacheada de configuración."""
    return Configuracion()


# Instancia global
config = obtener_config()
