from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.usuario import Usuario
from app.models.notificacion import Notificacion

router = APIRouter()


@router.get("/")
async def listar_mis_notificaciones(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notificacion)
        .where(Notificacion.usuario_id == current_user.id)
        .order_by(Notificacion.creado_en.desc())
        .limit(50)
    )
    notifs = result.scalars().all()

    datos = []
    for n in notifs:
        datos.append(
            {
                "id": str(n.id),
                "titulo": n.titulo,
                "mensaje": n.mensaje,
                "tipo": n.tipo,
                "leida": n.leida,
                "data_extra": n.data_extra,
                "creado_en": n.creado_en.isoformat(),
            }
        )
    return datos


@router.patch("/{id}/leer")
async def marcar_notificacion_leida(
    id: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notificacion).where(
            and_(Notificacion.id == id, Notificacion.usuario_id == current_user.id)
        )
    )
    n = result.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    n.leida = True
    await db.commit()
    return {"mensaje": "Notificación marcada como leída correctamente"}
