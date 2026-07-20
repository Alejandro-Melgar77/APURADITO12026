"""
Algoritmo de matching de rutas para pasajeros de Apuradito.
Usa consultas PostGIS para máxima eficiencia geoespacial.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from app.services.calculo_precio import (
    calcular_costo_viaje,
    calcular_score_ruta,
    obtener_config,
)


async def encontrar_rutas_optimas(
    lon_pasajero: float,
    lat_pasajero: float,
    lon_destino: float,
    lat_destino: float,
    db: AsyncSession,
    radio_max_m: Optional[float] = None,
    limite: Optional[int] = None,
) -> list[dict]:
    """Encuentra las rutas más óptimas para el pasajero usando PostGIS.

    PASOS:
    1. Filtrar rutas activas dentro del radio de caminata (ST_DWithin)
    2. Calcular punto de abordaje más cercano (ST_ClosestPoint)
    3. Calcular punto de desabordaje más cercano (ST_ClosestPoint)
    4. Verificar que abordaje esté ANTES del desabordaje en la ruta
    5. Calcular distancia del tramo del pasajero (ST_LineSubstring)
    6. Calcular costo y score de optimalidad
    7. Retornar top N rutas ordenadas por score DESC, costo ASC
    """
    config = await obtener_config(db)
    if radio_max_m is None:
        radio_max_m = float(config.get("radio_maximo_caminata_m", 800))
    if limite is None:
        limite = int(config.get("limite_rutas_pasajero", 10))

    # Consulta PostGIS principal
    # Usamos cast (::geometry) para funciones lineales y geography para distancias.
    query = text("""
        WITH rutas_candidatas AS (
            SELECT 
                rp.id,
                rp.conductor_id,
                rp.vehiculo_id,
                rp.origen_direccion,
                rp.destino_direccion,
                rp.asientos_disponibles,
                rp.estado,
                rp.hora_salida,
                rp.distancia_total_km,
                v.tipo AS tipo_vehiculo,
                v.combustible AS tipo_combustible,
                v.marca,
                v.modelo,
                v.color,
                v.placa,
                u.nombre || ' ' || u.apellido AS nombre_conductor,
                u.foto_perfil_url,
                c.calificacion_promedio,
                -- Punto de abordaje más cercano al pasajero (sobre geometry)
                ST_ClosestPoint(
                    rp.linea_ruta::geometry,
                    ST_SetSRID(ST_MakePoint(:lon_p, :lat_p), 4326)::geometry
                ) AS pto_abordaje,
                -- Distancia caminata al abordaje (metros)
                ST_Distance(
                    ST_SetSRID(ST_MakePoint(:lon_p, :lat_p), 4326)::geography,
                    rp.linea_ruta::geography
                ) AS dist_abordaje_m,
                -- Punto de desabordaje más cercano al destino
                ST_ClosestPoint(
                    rp.linea_ruta::geometry,
                    ST_SetSRID(ST_MakePoint(:lon_d, :lat_d), 4326)::geometry
                ) AS pto_desabordaje,
                -- Distancia caminata al destino (metros)
                ST_Distance(
                    ST_SetSRID(ST_MakePoint(:lon_d, :lat_d), 4326)::geography,
                    rp.linea_ruta::geography
                ) AS dist_desabordaje_m,
                -- Fracción en la ruta donde está el abordaje (0.0 a 1.0)
                ST_LineLocatePoint(
                    rp.linea_ruta::geometry,
                    ST_ClosestPoint(rp.linea_ruta::geometry, ST_SetSRID(ST_MakePoint(:lon_p, :lat_p), 4326)::geometry)
                ) AS frac_abordaje,
                -- Fracción en la ruta donde está el desabordaje (0.0 a 1.0)
                ST_LineLocatePoint(
                    rp.linea_ruta::geometry,
                    ST_ClosestPoint(rp.linea_ruta::geometry, ST_SetSRID(ST_MakePoint(:lon_d, :lat_d), 4326)::geometry)
                ) AS frac_desabordaje
            FROM rutas_publicadas rp
            JOIN vehiculos v ON rp.vehiculo_id = v.id
            JOIN conductores c ON rp.conductor_id = c.id
            JOIN usuarios u ON c.usuario_id = u.id
            WHERE 
                rp.estado IN ('programada', 'en_curso')
                AND rp.asientos_disponibles > 0
                AND rp.es_simulacion = FALSE
                AND rp.linea_ruta IS NOT NULL
                AND ST_DWithin(
                    rp.linea_ruta::geography,
                    ST_SetSRID(ST_MakePoint(:lon_p, :lat_p), 4326)::geography,
                    :radio_m
                )
        )
        SELECT rc.*,
            -- Distancia del tramo del viaje (metros → km)
            ST_Length(
                ST_LineSubstring(lr.linea_ruta::geometry, rc.frac_abordaje, rc.frac_desabordaje)::geography
            ) / 1000 AS distancia_viaje_km,
            -- Coordenadas del punto de abordaje
            ST_X(rc.pto_abordaje) AS lon_abordaje,
            ST_Y(rc.pto_abordaje) AS lat_abordaje,
            -- Coordenadas del punto de desabordaje
            ST_X(rc.pto_desabordaje) AS lon_desabordaje,
            ST_Y(rc.pto_desabordaje) AS lat_desabordaje
        FROM rutas_candidatas rc
        -- Unir con la geometría de la ruta para ST_LineSubstring
        JOIN rutas_publicadas lr ON lr.id = rc.id
        -- PASO CRÍTICO: descartar si el abordaje está DESPUÉS del desabordaje
        WHERE rc.frac_abordaje < rc.frac_desabordaje
    """)

    result = await db.execute(
        query,
        {
            "lon_p": lon_pasajero,
            "lat_p": lat_pasajero,
            "lon_d": lon_destino,
            "lat_d": lat_destino,
            "radio_m": radio_max_m,
        },
    )

    filas = result.mappings().all()
    rutas_procesadas = []

    for fila in filas:
        distancia_viaje = float(fila["distancia_viaje_km"] or 0)
        dist_abordaje = float(fila["dist_abordaje_m"] or 0)
        dist_desabordaje = float(fila["dist_desabordaje_m"] or 0)

        # Calcular costo del viaje
        costo_info = await calcular_costo_viaje(
            distancia_km=distancia_viaje,
            tipo_vehiculo=fila["tipo_vehiculo"],
            tipo_combustible=fila["tipo_combustible"],
            asientos_ocupados=1,  # 1 asiento para el pasajero
            db=db,
        )

        # Calcular score de optimalidad
        score = calcular_score_ruta(
            dist_caminata_abordaje_m=dist_abordaje,
            dist_caminata_desabordaje_m=dist_desabordaje,
            costo_bs=costo_info["costo_total_bs"],
        )

        rutas_procesadas.append(
            {
                "ruta_id": str(fila["id"]),
                "conductor": {
                    "nombre": fila["nombre_conductor"],
                    "foto_url": fila["foto_perfil_url"],
                    "calificacion": float(fila["calificacion_promedio"] or 0),
                },
                "vehiculo": {
                    "tipo": fila["tipo_vehiculo"],
                    "combustible": fila["tipo_combustible"],
                    "marca": fila["marca"],
                    "modelo": fila["modelo"],
                    "color": fila["color"],
                    "placa": fila["placa"],
                },
                "viaje": {
                    "origen_direccion": fila["origen_direccion"],
                    "destino_direccion": fila["destino_direccion"],
                    "hora_salida": fila["hora_salida"].isoformat()
                    if fila["hora_salida"]
                    else None,
                    "asientos_disponibles": fila["asientos_disponibles"],
                    "distancia_total_km": float(fila["distancia_total_km"] or 0),
                },
                "para_pasajero": {
                    "punto_abordaje": {
                        "lon": float(fila["lon_abordaje"]),
                        "lat": float(fila["lat_abordaje"]),
                    },
                    "punto_desabordaje": {
                        "lon": float(fila["lon_desabordaje"]),
                        "lat": float(fila["lat_desabordaje"]),
                    },
                    "distancia_caminata_abordaje_m": round(dist_abordaje, 1),
                    "distancia_caminata_desabordaje_m": round(dist_desabordaje, 1),
                    "distancia_viaje_km": round(distancia_viaje, 2),
                    "costo_bs": costo_info["costo_total_bs"],
                    "ganancia_conductor_bs": costo_info["ganancia_conductor_bs"],
                    "comision_app_bs": costo_info["comision_app_bs"],
                },
                "score_optimalidad": score,
            }
        )

    # Ordenar por score DESC, luego por costo ASC (desempate)
    rutas_procesadas.sort(
        key=lambda x: (-x["score_optimalidad"], x["para_pasajero"]["costo_bs"])
    )

    return rutas_procesadas[:limite]
