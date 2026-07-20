"""Punto de entrada principal de la aplicación Apuradito FastAPI."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.database import check_database_connection, init_db

# Importar routers
from app.api.v1 import (
    auth,
    usuarios,
    conductores,
    vehiculos,
    rutas,
    viajes,
    coins,
    configuracion,
    reportes,
    simulacion,
    politicas,
    reclamos,
    notificaciones,
    ia,
)
from app.websockets.viajes_ws import router as viajes_ws_router

# Configuración del logger
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación."""
    # Inicio
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Entorno: {settings.ENVIRONMENT}")
    # En desarrollo, crear tablas si no existen
    if settings.ENVIRONMENT == "local" or settings.AUTO_CREATE_SCHEMA:
        await init_db()
        logger.info("Base de datos inicializada de forma local")
    yield
    # Cierre
    logger.info("Apagando la aplicación...")


# Crear instancia de la aplicación
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de la plataforma de viajes compartidos Apuradito - Santa Cruz de la Sierra, Bolivia",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS and "*" not in settings.CORS_ORIGINS_LIST,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Estado"])
async def health_check():
    try:
        await check_database_connection()
    except Exception as exc:
        logger.exception("Database health check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible",
        ) from exc
    """Verificación de estado de la API."""
    return {
        "estado": "activo",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "entorno": settings.ENVIRONMENT,
    }


# Montar los routers de la API
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(
    usuarios.router, prefix="/api/v1/usuarios", tags=["Gestión de Usuarios"]
)
app.include_router(
    conductores.router, prefix="/api/v1/conductores", tags=["Gestión de Conductores"]
)
app.include_router(
    vehiculos.router, prefix="/api/v1/vehiculos", tags=["Gestión de Vehículos"]
)
app.include_router(rutas.router, prefix="/api/v1/rutas", tags=["Publicación de Rutas"])
app.include_router(
    viajes.router, prefix="/api/v1/viajes", tags=["Gestión de Viajes y Solicitudes"]
)
app.include_router(
    coins.router, prefix="/api/v1/coins", tags=["Sistema de Coins y Wallet"]
)
app.include_router(
    configuracion.router, prefix="/api/v1/configuracion", tags=["Configuración Global"]
)
app.include_router(
    reportes.router, prefix="/api/v1/reportes", tags=["Módulo de Reportes"]
)
app.include_router(
    simulacion.router, prefix="/api/v1/simulacion", tags=["Control del Simulador"]
)
app.include_router(
    politicas.router,
    prefix="/api/v1/politicas",
    tags=["Políticas Legales y Consentimientos"],
)
app.include_router(
    reclamos.router, prefix="/api/v1/reclamos", tags=["Reclamos y Denuncias"]
)
app.include_router(
    notificaciones.router,
    prefix="/api/v1/notificaciones",
    tags=["Notificaciones Push / Alertas"],
)
app.include_router(ia.router, prefix="/api/v1/ia", tags=["Inteligencia Artificial"])
app.include_router(viajes_ws_router, tags=["WebSockets"])
