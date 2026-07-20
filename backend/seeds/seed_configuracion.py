from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.configuracion_global import ConfiguracionGlobal
import logging

logger = logging.getLogger(__name__)

CONFIGURACION_INICIAL = [
    {"clave": "precio_gasolina_bs_litro", "valor": "6.50", "tipo": "float", "descripcion": "Precio de gasolina en bolivianos por litro"},
    {"clave": "precio_diesel_bs_litro", "valor": "3.72", "tipo": "float", "descripcion": "Precio de diésel en bolivianos por litro"},
    {"clave": "precio_gas_bs_metro_cubico", "valor": "2.50", "tipo": "float", "descripcion": "Precio del gas en bolivianos por metro cúbico"},
    {"clave": "consumo_automovil_gasolina_l_por_km", "valor": "0.08", "tipo": "float", "descripcion": "Consumo automóvil gasolina (litros/km)"},
    {"clave": "consumo_automovil_diesel_l_por_km", "valor": "0.065", "tipo": "float", "descripcion": "Consumo automóvil diésel (litros/km)"},
    {"clave": "consumo_automovil_gas_m3_por_km", "valor": "0.10", "tipo": "float", "descripcion": "Consumo automóvil gas (m³/km)"},
    {"clave": "consumo_moto_gasolina_l_por_km", "valor": "0.03", "tipo": "float", "descripcion": "Consumo moto gasolina (litros/km)"},
    {"clave": "tarifa_base_automovil_bs", "valor": "3.00", "tipo": "float", "descripcion": "Tarifa mínima por viaje en automóvil (Bs)"},
    {"clave": "tarifa_base_moto_bs", "valor": "2.00", "tipo": "float", "descripcion": "Tarifa mínima por viaje en moto (Bs)"},
    {"clave": "comision_app_porcentaje", "valor": "15.0", "tipo": "float", "descripcion": "Porcentaje que cobra la app por viaje"},
    {"clave": "tipo_cambio_bs_usd", "valor": "6.86", "tipo": "float", "descripcion": "Tipo de cambio boliviano a dólar"},
    {"clave": "radio_maximo_caminata_m", "valor": "800", "tipo": "int", "descripcion": "Radio máximo de caminata al punto de abordaje (metros)"},
    {"clave": "limite_rutas_pasajero", "valor": "10", "tipo": "int", "descripcion": "Cantidad máxima de rutas a mostrar al pasajero"},
    {"clave": "meses_morosidad_congelamiento", "valor": "2", "tipo": "int", "descripcion": "Meses sin pagar comisiones para congelar cuenta del conductor"},
    {"clave": "penalizacion_cancelacion_porcentaje", "valor": "10.0", "tipo": "float", "descripcion": "Porcentaje del viaje cobrado como penalización por cancelar"},
]

async def seed_configuracion(db: AsyncSession):
    logger.info("Insertando configuración global por defecto...")
    for item in CONFIGURACION_INICIAL:
        result = await db.execute(select(ConfiguracionGlobal).where(ConfiguracionGlobal.clave == item["clave"]))
        existing = result.scalar_one_or_none()
        
        if not existing:
            config = ConfiguracionGlobal(
                clave=item["clave"],
                valor=item["valor"],
                tipo=item["tipo"],
                descripcion=item["descripcion"]
            )
            db.add(config)
            
    await db.commit()
    logger.info("Configuraciones globales insertadas correctamente.")
