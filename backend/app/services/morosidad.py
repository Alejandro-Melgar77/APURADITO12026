from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from app.models.conductor import Conductor
from app.models.notificacion import Notificacion
from app.services.calculo_precio import obtener_config
import logging

logger = logging.getLogger(__name__)


async def verificar_y_congelar_morosos(db: AsyncSession):
    """Revisa conductores con comisiones pendientes que lleven morosos más de N meses."""
    logger.info("Iniciando revisión diaria de morosidad...")
    config = await obtener_config(db)
    meses_limite = int(config.get("meses_morosidad_congelamiento", 2))

    fecha_limite = datetime.now() - timedelta(days=meses_limite * 30)

    # Query: Conductores con comisiones pendientes de pago que no hayan sido congelados
    query = select(Conductor).where(
        and_(
            Conductor.comisiones_pendientes_bs > 0,
            Conductor.fecha_inicio_deuda.is_not(None),
            Conductor.fecha_inicio_deuda <= fecha_limite,
            ~Conductor.cuenta_congelada,
        )
    )

    result = await db.execute(query)
    conductores_morosos = result.scalars().all()

    congelados_count = 0
    for c in conductores_morosos:
        c.cuenta_congelada = True

        # Enviar notificación de congelamiento de cuenta
        notif = Notificacion(
            usuario_id=c.usuario_id,
            titulo="Cuenta Congelada por Morosidad",
            mensaje=f"Tu cuenta de conductor ha sido congelada debido a que presentas comisiones pendientes por más de {meses_limite} meses sin liquidar.",
            tipo="sistema",
            leida=False,
        )
        db.add(notif)
        congelados_count += 1

    await db.commit()
    logger.info(
        f"Revisión de morosidad completada. {congelados_count} conductores congelados."
    )
    return congelados_count
