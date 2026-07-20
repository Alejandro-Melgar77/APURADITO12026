from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.usuario import Usuario
from app.models.conductor import Conductor
from app.models.vehiculo import Vehiculo
from app.models.ruta_publicada import RutaPublicada
from app.schemas.ruta import (
    RutaPublicadaCreate,
    RutaPublicadaResponse,
    BuscarRutaRequest,
)
from app.services.matching_rutas import encontrar_rutas_optimas

router = APIRouter()


@router.post(
    "/", response_model=RutaPublicadaResponse, status_code=status.HTTP_201_CREATED
)
async def publicar_ruta(
    req: RutaPublicadaCreate,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Validar que sea conductor
    if current_user.rol not in ["conductor", "ambos"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los usuarios con perfil de conductor pueden publicar rutas",
        )

    # Obtener el conductor
    res_cond = await db.execute(
        select(Conductor).where(Conductor.usuario_id == current_user.id)
    )
    conductor = res_cond.scalar_one_or_none()

    if not conductor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Información de conductor no encontrada",
        )

    if conductor.cuenta_congelada:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta de conductor está temporalmente congelada por comisiones de viajes impagas.",
        )

    # Obtener el vehículo activo del conductor
    res_veh = await db.execute(
        select(Vehiculo).where(
            Vehiculo.conductor_id == conductor.id, Vehiculo.activo == True
        )
    )
    vehiculo = res_veh.scalar_one_or_none()

    if not vehiculo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes tener al menos un vehículo registrado y activo para publicar una ruta",
        )

    # Validar número de asientos disponibles (no puede superar los asientos del vehículo)
    # Para automóviles convencional el estándar son 4 disponibles (más el conductor = 5 totales).
    # En cualquier caso, no puede superar asientos_totales - 1 (para el conductor).
    asientos_maximos = vehiculo.asientos_totales - 1
    if req.asientos_disponibles > asientos_maximos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Los asientos disponibles ({req.asientos_disponibles}) no pueden superar la capacidad disponible de tu vehículo ({asientos_maximos})",
        )

    # Formatear geometrías a WKT con SRID 4326 para PostGIS
    origen_wkt = f"SRID=4326;POINT({req.origen_coor.lon} {req.origen_coor.lat})"
    destino_wkt = f"SRID=4326;POINT({req.destino_coor.lon} {req.destino_coor.lat})"

    linea_wkt = None
    if req.linea_ruta_coor:
        coords_str = ", ".join([f"{c.lon} {c.lat}" for c in req.linea_ruta_coor])
        linea_wkt = f"SRID=4326;LINESTRING({coords_str})"

    # Crear la ruta
    nueva_ruta = RutaPublicada(
        conductor_id=conductor.id,
        vehiculo_id=vehiculo.id,
        origen_punto=origen_wkt,
        origen_direccion=req.origen_direccion,
        destino_punto=destino_wkt,
        destino_direccion=req.destino_direccion,
        linea_ruta=linea_wkt,
        distancia_total_km=req.distancia_total_km,
        duracion_estimada_min=req.duracion_estimada_min,
        asientos_disponibles=req.asientos_disponibles,
        estado="programada",
        hora_salida=req.hora_salida,
        guardar_recorrido=req.guardar_recorrido,
        es_simulacion=req.es_simulacion,
    )

    db.add(nueva_ruta)
    await db.commit()
    await db.refresh(nueva_ruta)

    return nueva_ruta


@router.get("/", response_model=List[RutaPublicadaResponse])
async def listar_rutas(
    es_simulacion: Optional[bool] = False,
    estado: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(RutaPublicada).where(RutaPublicada.es_simulacion == es_simulacion)
    if estado:
        query = query.where(RutaPublicada.estado == estado)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{id}", response_model=RutaPublicadaResponse)
async def obtener_ruta(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RutaPublicada).where(RutaPublicada.id == id))
    ruta = result.scalar_one_or_none()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta


@router.post("/buscar")
async def buscar_rutas(req: BuscarRutaRequest, db: AsyncSession = Depends(get_db)):
    # Ejecutar algoritmo de matching
    rutas_optimas = await encontrar_rutas_optimas(
        lon_pasajero=req.lon_pasajero,
        lat_pasajero=req.lat_pasajero,
        lon_destino=req.lon_destino,
        lat_destino=req.lat_destino,
        db=db,
        radio_max_m=req.radio_max_m,
        limite=req.limite,
    )
    return rutas_optimas


@router.delete("/{id}")
async def cancelar_ruta(
    id: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(RutaPublicada).where(RutaPublicada.id == id))
    ruta = result.scalar_one_or_none()

    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    # Verificar que el usuario sea el dueño de la ruta
    res_cond = await db.execute(
        select(Conductor).where(Conductor.id == ruta.conductor_id)
    )
    conductor = res_cond.scalar_one_or_none()

    if not conductor or conductor.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cancelar esta ruta",
        )

    if ruta.estado not in ["programada", "en_curso"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede cancelar una ruta en estado: {ruta.estado}",
        )

    ruta.estado = "cancelada"
    await db.commit()
    return {"mensaje": "Ruta cancelada exitosamente"}
