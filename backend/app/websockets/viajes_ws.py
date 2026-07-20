import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import AsyncSessionLocal
from app.models.conductor import Conductor
from app.models.ruta_publicada import RutaPublicada
from app.websockets.manager import manager
from app.services.simulacion_engine import simulacion_engine

router = APIRouter()


@router.websocket("/ws/viajes")
async def websocket_viajes(websocket: WebSocket):
    await manager.connect(websocket, "viajes")
    try:
        while True:
            # Query active routes
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(RutaPublicada)
                    .options(
                        selectinload(RutaPublicada.conductor).selectinload(Conductor.usuario),
                        selectinload(RutaPublicada.vehiculo),
                    )
                    .where(RutaPublicada.estado == "en_curso")
                )
                rutas = result.scalars().all()

                lista_rutas = []
                for r in rutas:
                    ruta_dict = {
                        "id": str(r.id),
                        "conductor_nombre": r.conductor.usuario.nombre
                        if r.conductor and r.conductor.usuario
                        else "Desconocido",
                        "conductor_apellido": r.conductor.usuario.apellido
                        if r.conductor and r.conductor.usuario
                        else "",
                        "vehiculo_placa": r.vehiculo.placa
                        if r.vehiculo
                        else "Desconocido",
                        "vehiculo_color": r.vehiculo.color
                        if r.vehiculo
                        else "Desconocido",
                        "origen_direccion": r.origen_direccion,
                        "destino_direccion": r.destino_direccion,
                        "asientos_disponibles": r.asientos_disponibles,
                        "estado": r.estado,
                        "hora_salida": r.hora_salida.isoformat(),
                        "es_simulacion": r.es_simulacion,
                    }

                    if str(r.id) in simulacion_engine.posiciones_activas:
                        pos = simulacion_engine.posiciones_activas[str(r.id)]
                        ruta_dict["lat"] = pos["lat"]
                        ruta_dict["lng"] = pos["lng"]
                        ruta_dict["ruta_geojson"] = pos.get("ruta_geojson", [])

                    lista_rutas.append(ruta_dict)

                await websocket.send_text(
                    json.dumps(
                        {
                            "tipo": "viajes_activos",
                            "data": lista_rutas,
                            "timestamp": str(datetime.utcnow()),
                        }
                    )
                )

            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket, "viajes")
