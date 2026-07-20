from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_admin
from app.models.usuario import Usuario
from app.models.reclamo import Reclamo

router = APIRouter()


class ReclamoCreate(BaseModel):
    solicitud_viaje_id: Optional[str] = None
    tipo: str  # 'reclamo', 'denuncia', 'sugerencia'
    asunto: str
    descripcion: str


@router.get("/")
async def listar_reclamos(
    tipo: Optional[str] = Query(
        None, description="Filtrar por tipo: reclamo, denuncia, sugerencia"
    ),
    estado: Optional[str] = Query(
        None, description="Filtrar por estado: abierto, en_revision, resuelto, cerrado"
    ),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Reclamo)

    if tipo:
        query = query.where(Reclamo.tipo == tipo)
    if estado:
        query = query.where(Reclamo.estado == estado)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (pagina - 1) * por_pagina
    query = query.order_by(Reclamo.creado_en.desc()).offset(offset).limit(por_pagina)

    result = await db.execute(query)
    reclamos = result.scalars().all()

    datos = []
    for r in reclamos:
        datos.append(
            {
                "id": str(r.id),
                "usuario": f"{r.usuario.nombre} {r.usuario.apellido}",
                "solicitud_viaje_id": str(r.solicitud_viaje_id)
                if r.solicitud_viaje_id
                else None,
                "tipo": r.tipo,
                "asunto": r.asunto,
                "descripcion": r.descripcion,
                "estado": r.estado,
                "creado_en": r.creado_en.isoformat(),
            }
        )

    return {"datos": datos, "total": total, "pagina": pagina, "por_pagina": por_pagina}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def registrar_reclamo(
    req: ReclamoCreate,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if req.tipo not in ["reclamo", "denuncia", "sugerencia"]:
        raise HTTPException(status_code=400, detail="Tipo de reclamo no válido")

    nuevo_reclamo = Reclamo(
        usuario_id=current_user.id,
        solicitud_viaje_id=req.solicitud_viaje_id,
        tipo=req.tipo,
        asunto=req.asunto,
        descripcion=req.descripcion,
        estado="abierto",
    )
    db.add(nuevo_reclamo)
    await db.commit()
    await db.refresh(nuevo_reclamo)
    return {
        "mensaje": "Reclamo registrado exitosamente",
        "reclamo_id": str(nuevo_reclamo.id),
    }


@router.get("/{id}")
async def obtener_reclamo(
    id: str,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Reclamo).where(Reclamo.id == id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Reclamo no encontrado")

    return {
        "id": str(r.id),
        "usuario_id": str(r.usuario_id),
        "usuario": f"{r.usuario.nombre} {r.usuario.apellido}",
        "email": r.usuario.email,
        "telefono": r.usuario.telefono,
        "solicitud_viaje_id": str(r.solicitud_viaje_id)
        if r.solicitud_viaje_id
        else None,
        "tipo": r.tipo,
        "asunto": r.asunto,
        "descripcion": r.descripcion,
        "estado": r.estado,
        "creado_en": r.creado_en.isoformat(),
    }


@router.patch("/{id}/estado")
async def cambiar_estado_reclamo(
    id: str,
    estado: str,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if estado not in ["abierto", "en_revision", "resuelto", "cerrado"]:
        raise HTTPException(status_code=400, detail="Estado de reclamo no válido")

    result = await db.execute(select(Reclamo).where(Reclamo.id == id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Reclamo no encontrado")

    r.estado = estado
    await db.commit()
    return {"mensaje": f"Estado del reclamo cambiado a {estado} exitosamente"}
