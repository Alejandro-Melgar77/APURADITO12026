"""Central runtime configuration for the Apuradito API."""

from functools import lru_cache
from typing import List, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "local"

    DATABASE_URL_LOCAL: str = (
        "postgresql+asyncpg://apuradito_user:apuradito_pass_dev@localhost:5432/apuradito_db"
    )
    DATABASE_URL_PRODUCTION: str = ""
    DATABASE_URL: Optional[str] = None
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 5
    AUTO_CREATE_SCHEMA: bool = False

    REDIS_URL: str = "redis://localhost:6379"

    SECRET_KEY: str = "cambia_esta_clave_secreta_en_produccion_minimo_32_caracteres"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000,"
        "http://127.0.0.1:5173,http://127.0.0.1:3000"
    )
    CORS_ALLOW_CREDENTIALS: bool = True

    FIREBASE_PROJECT_ID: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "Apuradito <apuradito.app@gmail.com>"

    APP_NAME: str = "Apuradito"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    @model_validator(mode="after")
    def validate_runtime_configuration(self) -> "Settings":
        """Resolve environment values and reject unsafe production settings."""
        database_url = self.DATABASE_URL or (
            self.DATABASE_URL_PRODUCTION
            if self.ENVIRONMENT == "production"
            else self.DATABASE_URL_LOCAL
        )
        # Supabase shows a plain PostgreSQL URI, while SQLAlchemy async needs
        # the asyncpg driver prefix.
        if database_url.startswith("postgres://"):
            database_url = "postgresql+asyncpg://" + database_url.removeprefix("postgres://")
        elif database_url.startswith("postgresql://"):
            database_url = "postgresql+asyncpg://" + database_url.removeprefix("postgresql://")
        self.DATABASE_URL = database_url

        if self.ENVIRONMENT == "production":
            if not self.DATABASE_URL:
                raise ValueError("DATABASE_URL es obligatoria en produccion")
            if (
                self.SECRET_KEY
                == "cambia_esta_clave_secreta_en_produccion_minimo_32_caracteres"
                or len(self.SECRET_KEY) < 32
            ):
                raise ValueError("SECRET_KEY debe ser unica y tener al menos 32 caracteres")
            # Auto-desactivar DEBUG por seguridad
            self.DEBUG = False
        return self

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        return [
            origin.strip().rstrip("/")
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
