import random
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from app.api.deps import get_current_admin
from app.core.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.models.conductor import Conductor
from app.models.vehiculo import Vehiculo
from app.models.ruta_publicada import RutaPublicada
from app.services.simulacion_engine import simulacion_engine

router = APIRouter()


class IniciarSimulacionRequest(BaseModel):
    num_vehiculos: int = Field(..., ge=1, le=20)
    num_pasajeros: int = Field(..., ge=0, le=200)
    velocidad_promedio: float = Field(..., gt=0, le=120)
    origen_lat: Optional[float] = None
    origen_lng: Optional[float] = None
    destino_lat: Optional[float] = None
    destino_lng: Optional[float] = None

class VelocidadSimulacionRequest(BaseModel):
    velocidad_kmh: float = Field(..., gt=0, le=120)


ESTADO_SIMULACION = {
    "activo": False,
    "num_vehiculos": 0,
    "num_pasajeros": 0,
    "velocidad_promedio": 40.0,
}


def generar_punto():
    # Coordenadas aproximadas de Santa Cruz
    return {
        "lat": random.uniform(-17.83, -17.76),
        "lng": random.uniform(-63.21, -63.12),
    }


@router.post("/iniciar")
async def iniciar_simulacion(
    req: IniciarSimulacionRequest, current_user: Usuario = Depends(get_current_admin)
):
    if ESTADO_SIMULACION["activo"]:
        raise HTTPException(status_code=409, detail="Ya hay una simulacion activa")
    if (req.origen_lat is None) != (req.origen_lng is None):
        raise HTTPException(
            status_code=422,
            detail="Origen requiere latitud y longitud juntas",
        )
    if (req.destino_lat is None) != (req.destino_lng is None):
        raise HTTPException(
            status_code=422,
            detail="Destino requiere latitud y longitud juntas",
        )

    async with AsyncSessionLocal() as session:
        # Obtenemos conductores
        result_conductores = await session.execute(
            select(Conductor)
            .limit(max(10, req.num_vehiculos))
        )
        conductores = result_conductores.scalars().all()

        if not conductores:
            # Fallback en caso no haya conductores aprobados, buscar cualquiera
            result_conductores_all = await session.execute(
                select(Conductor).limit(max(10, req.num_vehiculos))
            )
            conductores = result_conductores_all.scalars().all()
            if not conductores:
                raise HTTPException(
                    status_code=400, detail="No hay conductores para simular."
                )

        rutas_creadas = 0
        for i in range(req.num_vehiculos):
            conductor = random.choice(conductores)

            result_vehiculos = await session.execute(
                select(Vehiculo).where(Vehiculo.conductor_id == conductor.id).limit(1)
            )
            vehiculo = result_vehiculos.scalar_one_or_none()
            if not vehiculo:
                # Si no tiene, busca cualquier vehiculo (para fines de simulacion)
                result_vehiculos_all = await session.execute(select(Vehiculo).limit(1))
                vehiculo = result_vehiculos_all.scalar_one_or_none()
                if not vehiculo:
                    continue

            if req.num_vehiculos > 1 or req.origen_lat is None:
                origen = generar_punto()
                destino = generar_punto()
                o_lat, o_lng = origen["lat"], origen["lng"]
                d_lat, d_lng = destino["lat"], destino["lng"]
            else:
                o_lat, o_lng = req.origen_lat, req.origen_lng
                d_lat, d_lng = req.destino_lat, req.destino_lng
                if req.destino_lat is None:
                    destino = generar_punto()
                    d_lat, d_lng = destino["lat"], destino["lng"]

            ruta = RutaPublicada(
                conductor_id=conductor.id,
                vehiculo_id=vehiculo.id,
                origen_punto=f"SRID=4326;POINT({o_lng} {o_lat})",
                destino_punto=f"SRID=4326;POINT({d_lng} {d_lat})",
                origen_direccion="Origen Simulado",
                destino_direccion="Destino Simulado",
                asientos_disponibles=4,
                estado="en_curso",
                hora_salida=datetime.utcnow(),
                hora_llegada_estimada=datetime.utcnow() + timedelta(minutes=30),
                es_simulacion=True,
            )
            session.add(ruta)
            await session.flush()

            # Registrar en engine
            await simulacion_engine.registrar_ruta(
                ruta_id=ruta.id,
                lat=o_lat,
                lng=o_lng,
                dest_lat=d_lat,
                dest_lng=d_lng,
                vel=req.velocidad_promedio,
            )
            rutas_creadas += 1

        await session.commit()

    ESTADO_SIMULACION["activo"] = True
    ESTADO_SIMULACION["num_vehiculos"] = rutas_creadas
    ESTADO_SIMULACION["num_pasajeros"] = req.num_pasajeros
    ESTADO_SIMULACION["velocidad_promedio"] = req.velocidad_promedio

    return {
        "mensaje": f"Simulación iniciada con {rutas_creadas} rutas",
        "estado": ESTADO_SIMULACION,
    }


@router.post("/detener")
async def detener_simulacion(current_user: Usuario = Depends(get_current_admin)):
    ESTADO_SIMULACION["activo"] = False
    ESTADO_SIMULACION["num_vehiculos"] = 0
    ESTADO_SIMULACION["num_pasajeros"] = 0
    simulacion_engine.detener()

    # Eliminar rutas de simulacion en BD
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(RutaPublicada).where(RutaPublicada.es_simulacion)
        )
        rutas_sim = result.scalars().all()
        for r in rutas_sim:
            await session.delete(r)
        await session.commit()

    return {"mensaje": "Simulación detenida", "estado": ESTADO_SIMULACION}


@router.get("/estado")
async def obtener_estado_simulacion():
    estado = ESTADO_SIMULACION.copy()
    estado["rutas_activas"] = len(simulacion_engine.posiciones_activas)
    return estado

@router.patch("/velocidad")
async def actualizar_velocidad(
    req: VelocidadSimulacionRequest, current_user: Usuario = Depends(get_current_admin)
):
    if not ESTADO_SIMULACION["activo"]:
        raise HTTPException(status_code=400, detail="La simulación no está activa")
    ESTADO_SIMULACION["velocidad_promedio"] = req.velocidad_kmh
    simulacion_engine.actualizar_velocidad_global(req.velocidad_kmh)
    return {"mensaje": f"Velocidad global actualizada a {req.velocidad_kmh} km/h"}
