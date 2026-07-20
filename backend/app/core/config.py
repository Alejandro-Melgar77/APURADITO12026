"""Configuración central de la aplicación Apuradito."""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Entorno de ejecución
    ENVIRONMENT: str = "local"  # "local" o "production"

    # Base de datos
    DATABASE_URL_LOCAL: str = "postgresql+asyncpg://apuradito_user:apuradito_pass_dev@localhost:5432/apuradito_db"
    DATABASE_URL_PRODUCTION: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    SECRET_KEY: str = "cambia_esta_clave_secreta_en_produccion_minimo_32_caracteres"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"

    # Firebase
    FIREBASE_PROJECT_ID: str = ""

    # Email SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "Apuradito <apuradito.app@gmail.com>"

    # App
    APP_NAME: str = "Apuradito"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    @property
    def DATABASE_URL(self) -> str:
        """Retorna la URL de BD según el entorno activo."""
        if self.ENVIRONMENT == "production":
            import os
            return os.getenv("DATABASE_URL", self.DATABASE_URL_PRODUCTION) or self.DATABASE_URL_LOCAL
        return self.DATABASE_URL_LOCAL

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """Retorna lista de orígenes CORS."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    """Retorna instancia cacheada de la configuración."""
    return Settings()


settings = get_settings()
