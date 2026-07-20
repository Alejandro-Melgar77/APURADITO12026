from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from geoalchemy2.shape import to_shape
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.usuario import Usuario
from app.models.conductor import Conductor
from app.models.vehiculo import Vehiculo
from app.models.ruta_publicada import RutaPublicada
from app.models.solicitud_viaje import SolicitudViaje
from app.schemas.ruta import (
    RutaPublicadaCreate,
    RutaPublicadaResponse,
    BuscarRutaRequest,
)
from app.services.matching_rutas import encontrar_rutas_optimas

router = APIRouter()


def _coordenada_geografica(valor):
    """Convierte una geometria PostGIS a coordenadas serializables para clientes."""
    if valor is None:
        return None
    punto = to_shape(valor)
    return {"lat": punto.y, "lng": punto.x}


def _linea_geografica(valor):
    if valor is None:
        return []
    linea = to_shape(valor)
    return [[longitud, latitud] for longitud, latitud in linea.coords]


def _ruta_para_movil(ruta: RutaPublicada) -> dict:
    """Devuelve la informacion que necesita el mapa sin exponer datos privados."""
    conductor = ruta.conductor.usuario if ruta.conductor else None
    vehiculo = ruta.vehiculo
    origen = _coordenada_geografica(ruta.origen_punto)
    destino = _coordenada_geografica(ruta.destino_punto)
    return {
        "id": str(ruta.id),
        "conductor_nombre": conductor.nombre if conductor else "Conductor",
        "conductor_apellido": conductor.apellido if conductor else "",
        "vehiculo_placa": vehiculo.placa if vehiculo else None,
        "vehiculo_color": vehiculo.color if vehiculo else None,
        "origen_direccion": ruta.origen_direccion or "Origen",
        "destino_direccion": ruta.destino_direccion or "Destino",
        "origen_lat": origen["lat"] if origen else None,
        "origen_lng": origen["lng"] if origen else None,
        "destino_lat": destino["lat"] if destino else None,
        "destino_lng": destino["lng"] if destino else None,
        "asientos_disponibles": ruta.asientos_disponibles,
        "estado": ruta.estado,
        "hora_salida": ruta.hora_salida.isoformat(),
        "es_simulacion": ruta.es_simulacion,
        "ruta_geojson": _linea_geografica(ruta.linea_ruta),
        "distancia_total_km": float(ruta.distancia_total_km or 0),
        "duracion_estimada_min": ruta.duracion_estimada_min,
    }


async def _obtener_ruta_del_conductor(
    ruta_id: str, current_user: Usuario, db: AsyncSession
) -> RutaPublicada:
    resultado = await db.execute(
        select(RutaPublicada)
        .options(selectinload(RutaPublicada.conductor))
        .where(RutaPublicada.id == ruta_id)
    )
    ruta = resultado.scalar_one_or_none()
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    if not ruta.conductor or ruta.conductor.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos sobre esta ruta")
    return ruta


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
            Vehiculo.conductor_id == conductor.id, Vehiculo.activo.is_(True)
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


@router.get("/disponibles")
async def listar_rutas_disponibles_movil(db: AsyncSession = Depends(get_db)):
    """Rutas publicables para el mapa de pasajeros, con geometria y conductor."""
    resultado = await db.execute(
        select(RutaPublicada)
        .options(
            selectinload(RutaPublicada.conductor).selectinload(Conductor.usuario),
            selectinload(RutaPublicada.vehiculo),
        )
        .where(
            RutaPublicada.es_simulacion.is_(False),
            RutaPublicada.estado.in_(["programada", "en_curso"]),
        )
        .order_by(RutaPublicada.hora_salida.asc())
    )
    return [_ruta_para_movil(ruta) for ruta in resultado.scalars().all()]


@router.get("/mias", response_model=List[RutaPublicadaResponse])
async def listar_mis_rutas(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(
        select(RutaPublicada)
        .join(Conductor, RutaPublicada.conductor_id == Conductor.id)
        .where(Conductor.usuario_id == current_user.id)
        .order_by(RutaPublicada.hora_salida.desc())
    )
    return resultado.scalars().all()


@router.post("/{id}/iniciar", response_model=RutaPublicadaResponse)
async def iniciar_ruta(
    id: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    ruta = await _obtener_ruta_del_conductor(id, current_user, db)
    if ruta.estado != "programada":
        raise HTTPException(
            status_code=400,
            detail="Solo se puede iniciar una ruta programada",
        )
    ruta.estado = "en_curso"
    await db.commit()
    await db.refresh(ruta)
    return ruta


@router.post("/{id}/finalizar", response_model=RutaPublicadaResponse)
async def finalizar_ruta(
    id: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    ruta = await _obtener_ruta_del_conductor(id, current_user, db)
    if ruta.estado != "en_curso":
        raise HTTPException(
            status_code=400,
            detail="La ruta debe estar en curso para finalizarla",
        )
    pendientes = await db.scalar(
        select(func.count())
        .select_from(SolicitudViaje)
        .where(
            SolicitudViaje.ruta_publicada_id == ruta.id,
            SolicitudViaje.estado.in_(["pendiente", "aceptada"]),
        )
    )
    if pendientes:
        raise HTTPException(
            status_code=400,
            detail="Gestiona o completa todas las solicitudes antes de finalizar la ruta",
        )
    ruta.estado = "completada"
    await db.commit()
    await db.refresh(ruta)
    return ruta


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
