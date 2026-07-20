import asyncio
import logging
from app.core.database import AsyncSessionLocal
from seeds.seed_configuracion import seed_configuracion
from seeds.seed_usuarios import seed_usuarios

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def run_all():
    logger.info("Iniciando ejecución de semillas (seeds) para base de datos...")
    async with AsyncSessionLocal() as db:
        try:
            # 1. Poblar configuración global
            await seed_configuracion(db)
            # 2. Poblar usuarios de prueba
            await seed_usuarios(db)
            logger.info("¡Todas las semillas se ejecutaron exitosamente!")
        except Exception as e:
            logger.error(f"Error al ejecutar las semillas: {str(e)}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(run_all())
