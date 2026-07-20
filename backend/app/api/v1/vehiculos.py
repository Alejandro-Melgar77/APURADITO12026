from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo

router = APIRouter()


@router.get("/")
async def listar_vehiculos(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo: automovil, moto"),
    placa: Optional[str] = Query(None, description="Buscar por placa"),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Vehiculo)

    if tipo:
        query = query.where(Vehiculo.tipo == tipo)
    if placa:
        query = query.where(Vehiculo.placa.ilike(f"%{placa}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (pagina - 1) * por_pagina
    query = query.order_by(Vehiculo.creado_en.desc()).offset(offset).limit(por_pagina)

    result = await db.execute(query)
    vehiculos = result.scalars().all()

    datos = []
    for v in vehiculos:
        datos.append(
            {
                "id": str(v.id),
                "conductor_id": str(v.conductor_id),
                "placa": v.placa,
                "marca": v.marca,
                "modelo": v.modelo,
                "color": v.color,
                "anio": v.anio,
                "tipo": v.tipo,
                "combustible": v.combustible,
                "asientos_totales": v.asientos_totales,
                "placa_verificada": v.placa_verificada,
                "activo": v.activo,
                "creado_en": v.creado_en.isoformat(),
            }
        )

    return {"datos": datos, "total": total, "pagina": pagina, "por_pagina": por_pagina}


@router.get("/{id}")
async def obtener_vehiculo(
    id: str,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Vehiculo).where(Vehiculo.id == id))
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    return {
        "id": str(v.id),
        "conductor_id": str(v.conductor_id),
        "placa": v.placa,
        "marca": v.marca,
        "modelo": v.modelo,
        "color": v.color,
        "anio": v.anio,
        "tipo": v.tipo,
        "combustible": v.combustible,
        "asientos_totales": v.asientos_totales,
        "foto_placa_url": v.foto_placa_url,
        "placa_detectada_ia": v.placa_detectada_ia,
        "placa_verificada": v.placa_verificada,
        "activo": v.activo,
        "creado_en": v.creado_en.isoformat(),
    }


@router.patch("/{id}/verificar-placa")
async def verificar_placa_vehiculo(
    id: str,
    verificada: bool,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Vehiculo).where(Vehiculo.id == id))
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    v.placa_verificada = verificada
    await db.commit()
    return {"mensaje": f"Estado de verificación de placa actualizado a: {verificada}"}


@router.patch("/{id}/activo")
async def cambiar_estado_activo_vehiculo(
    id: str,
    activo: bool,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Vehiculo).where(Vehiculo.id == id))
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    v.activo = activo
    await db.commit()
    return {"mensaje": f"Estado activo del vehículo cambiado a: {activo}"}
