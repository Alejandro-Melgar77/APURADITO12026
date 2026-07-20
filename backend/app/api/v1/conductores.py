from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.usuario import Usuario
from app.models.conductor import Conductor
from app.models.vehiculo import Vehiculo

router = APIRouter()


@router.get("/")
async def listar_conductores(
    estado_cuenta: Optional[str] = Query(
        None, description="Filtrar por estado: activo, congelado"
    ),
    busqueda: Optional[str] = Query(
        None, description="Buscar por nombre o carnet del conductor"
    ),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Conductor)
        .join(Usuario, Conductor.usuario_id == Usuario.id)
        .where(Usuario.estado != "eliminado")
    )

    if estado_cuenta == "congelado":
        query = query.where(Conductor.cuenta_congelada == True)
    elif estado_cuenta == "activo":
        query = query.where(Conductor.cuenta_congelada == False)

    if busqueda:
        busqueda_like = f"%{busqueda}%"
        query = query.where(
            (Usuario.nombre.ilike(busqueda_like))
            | (Usuario.apellido.ilike(busqueda_like))
            | (Usuario.ci_carnet.ilike(busqueda_like))
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (pagina - 1) * por_pagina
    query = query.offset(offset).limit(por_pagina)

    result = await db.execute(query)
    conductores = result.scalars().all()

    datos = []
    for c in conductores:
        datos.append(
            {
                "conductor_id": str(c.id),
                "nombre": f"{c.usuario.nombre} {c.usuario.apellido}",
                "email": c.usuario.email,
                "ci_carnet": c.usuario.ci_carnet,
                "calificacion_promedio": float(c.calificacion_promedio or 0),
                "total_viajes": c.total_viajes,
                "km_totales": float(c.km_totales or 0),
                "comisiones_pendientes_bs": float(c.comisiones_pendientes_bs or 0),
                "cuenta_congelada": c.cuenta_congelada,
                "congelado_manualmente": c.congelado_manualmente,
                "verificado_facial": c.usuario.verificado_facial,
                "estado_usuario": c.usuario.estado,
            }
        )

    return {"datos": datos, "total": total, "pagina": pagina, "por_pagina": por_pagina}


@router.get("/{id}")
async def obtener_conductor(
    id: str,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Conductor).where(Conductor.id == id))
    c = result.scalar_one_or_none()

    if not c or c.usuario.estado == "eliminado":
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    return {
        "conductor_id": str(c.id),
        "usuario_id": str(c.usuario_id),
        "nombre": f"{c.usuario.nombre} {c.usuario.apellido}",
        "email": c.usuario.email,
        "ci_carnet": c.usuario.ci_carnet,
        "telefono": c.usuario.telefono,
        "foto_perfil_url": c.usuario.foto_perfil_url,
        "foto_facial_verificacion_url": c.usuario.foto_facial_verificacion_url,
        "calificacion_promedio": float(c.calificacion_promedio or 0),
        "total_viajes": c.total_viajes,
        "km_totales": float(c.km_totales or 0),
        "comisiones_pendientes_bs": float(c.comisiones_pendientes_bs or 0),
        "cuenta_congelada": c.cuenta_congelada,
        "congelado_manualmente": c.congelado_manualmente,
        "verificado_facial": c.usuario.verificado_facial,
        "estado_usuario": c.usuario.estado,
        "creado_en": c.creado_en.isoformat(),
    }


@router.patch("/{id}/verificar-facial")
async def verificar_facial_conductor(
    id: str,
    verificado: bool,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Conductor).where(Conductor.id == id))
    c = result.scalar_one_or_none()

    if not c:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    c.usuario.verificado_facial = verificado

    # Si se verifica correctamente y el estado era pendiente, lo activamos
    if verificado and c.usuario.estado == "pendiente":
        c.usuario.estado = "activo"

    await db.commit()
    return {"mensaje": f"Estado de verificación facial actualizado a: {verificado}"}


@router.patch("/{id}/congelar")
async def congelar_cuenta_conductor(
    id: str,
    congelar: bool,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Conductor).where(Conductor.id == id))
    c = result.scalar_one_or_none()

    if not c:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    c.cuenta_congelada = congelar
    c.congelado_manualmente = congelar

    await db.commit()
    estado_txt = "congelada" if congelar else "descongelada"
    return {"mensaje": f"La cuenta del conductor ha sido {estado_txt} de forma manual."}


@router.post("/verificar-morosidad")
async def verificar_morosidad_conductores(
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.services.morosidad import verificar_y_congelar_morosos

    congelados = await verificar_y_congelar_morosos(db)
    return {
        "mensaje": "Revisión de morosidad realizada",
        "conductores_congelados": congelados,
    }


@router.get("/{id}/vehiculos")
async def listar_vehiculos_conductor(id: str, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Vehiculo).where(Vehiculo.conductor_id == id))
    vehiculos = result.scalars().all()

    datos = []
    for v in vehiculos:
        datos.append(
            {
                "id": str(v.id),
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
            }
        )
    return datos
