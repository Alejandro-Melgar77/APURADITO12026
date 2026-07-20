"""
Servicio de cálculo de precios para viajes Apuradito.
Todas las variables se leen de la tabla configuracion_global — nunca hardcodeadas.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.configuracion_global import ConfiguracionGlobal


async def obtener_config(db: AsyncSession) -> dict:
    """Carga todos los valores de configuración como diccionario tipado."""
    result = await db.execute(select(ConfiguracionGlobal))
    configs = result.scalars().all()
    valores = {}
    for config in configs:
        if config.tipo == "float":
            valores[config.clave] = float(config.valor)
        elif config.tipo == "int":
            valores[config.clave] = int(config.valor)
        else:
            valores[config.clave] = config.valor
    return valores


async def calcular_costo_combustible_por_km(
    tipo_vehiculo: str,  # 'automovil' o 'moto'
    tipo_combustible: str,  # 'gasolina', 'diesel', 'gas'
    config: dict,
) -> float:
    """Calcula el costo de combustible por kilómetro.

    Fórmula: costo_km = consumo_l_por_km × precio_bs_litro
    """
    # Obtener consumo del vehículo
    if tipo_combustible == "gas":
        clave_consumo = f"consumo_{tipo_vehiculo}_gas_m3_por_km"
        clave_precio = "precio_gas_bs_metro_cubico"
    else:
        clave_consumo = f"consumo_{tipo_vehiculo}_{tipo_combustible}_l_por_km"
        clave_precio = f"precio_{tipo_combustible}_bs_litro"

    consumo = config.get(clave_consumo, 0.08)  # default seguro
    precio = config.get(clave_precio, 6.50)  # default seguro

    return round(float(consumo) * float(precio), 4)


async def calcular_costo_viaje(
    distancia_km: float,
    tipo_vehiculo: str,
    tipo_combustible: str,
    asientos_ocupados: int,
    db: AsyncSession,
) -> dict:
    """Calcula el costo completo de un viaje.

    Fórmula Maestra:
        costo_combustible = distancia_km × costo_combustible_por_km
        tarifa_base = config[tarifa_base_{tipo_vehiculo}_bs]
        subtotal = costo_combustible + tarifa_base
        costo_por_pasajero = subtotal / max(asientos_ocupados, 1)
        comision_app = costo_por_pasajero × (comision_app_% / 100)
        ganancia_conductor = costo_por_pasajero - comision_app

    Retorna:
        dict con costo_total_bs, comision_app_bs, ganancia_conductor_bs,
        costo_combustible_bs, distancia_km, tarifa_base_bs
    """
    config = await obtener_config(db)

    costo_km = await calcular_costo_combustible_por_km(
        tipo_vehiculo, tipo_combustible, config
    )
    costo_combustible = round(distancia_km * costo_km, 2)

    tarifa_base = float(config.get(f"tarifa_base_{tipo_vehiculo}_bs", 3.00))
    subtotal = round(costo_combustible + tarifa_base, 2)

    asientos = max(asientos_ocupados, 1)
    costo_por_pasajero = round(subtotal / asientos, 2)

    comision_porcentaje = float(config.get("comision_app_porcentaje", 15.0))
    comision_app = round(costo_por_pasajero * (comision_porcentaje / 100), 2)
    ganancia_conductor = round(costo_por_pasajero - comision_app, 2)

    return {
        "costo_total_bs": costo_por_pasajero,
        "comision_app_bs": comision_app,
        "ganancia_conductor_bs": ganancia_conductor,
        "costo_combustible_bs": costo_combustible,
        "tarifa_base_bs": tarifa_base,
        "distancia_km": distancia_km,
        "asientos_ocupados": asientos,
    }


async def calcular_penalizacion(costo_viaje_bs: float, db: AsyncSession) -> float:
    """Calcula la penalización por cancelación de viaje.

    Fórmula: penalizacion = costo_viaje_bs × (penalizacion_% / 100)
    """
    config = await obtener_config(db)
    porcentaje = float(config.get("penalizacion_cancelacion_porcentaje", 10.0))
    return round(costo_viaje_bs * (porcentaje / 100), 2)


def calcular_score_ruta(
    dist_caminata_abordaje_m: float, dist_caminata_desabordaje_m: float, costo_bs: float
) -> float:
    """Calcula el score de optimalidad de una ruta para el pasajero.

    Fórmula:
        score = (1000 / (dist_abordaje + 1)) × 0.4
              + (1000 / (dist_desabordaje + 1)) × 0.4
              + (100 / (costo + 1)) × 0.2

    Mayor score = más óptima la ruta para el pasajero.
    """
    score = (
        (1000 / (dist_caminata_abordaje_m + 1)) * 0.4
        + (1000 / (dist_caminata_desabordaje_m + 1)) * 0.4
        + (100 / (costo_bs + 1)) * 0.2
    )
    return round(score, 4)
