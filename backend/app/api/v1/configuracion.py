from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.core.database import get_db
from app.models.configuracion_global import ConfiguracionGlobal
from app.models.usuario import Usuario
from app.api.deps import get_current_admin

router = APIRouter()


class ActualizarConfiguracionRequest(BaseModel):
    valor: str


# Configuración inicial del seed para reset
CONFIGURACION_INICIAL = [
    {
        "clave": "precio_gasolina_bs_litro",
        "valor": "6.50",
        "tipo": "float",
        "descripcion": "Precio de gasolina en bolivianos por litro",
    },
    {
        "clave": "precio_diesel_bs_litro",
        "valor": "3.72",
        "tipo": "float",
        "descripcion": "Precio de diésel en bolivianos por litro",
    },
    {
        "clave": "precio_gas_bs_metro_cubico",
        "valor": "2.50",
        "tipo": "float",
        "descripcion": "Precio del gas en bolivianos por metro cúbico",
    },
    {
        "clave": "consumo_automovil_gasolina_l_por_km",
        "valor": "0.08",
        "tipo": "float",
        "descripcion": "Consumo automóvil gasolina (litros/km)",
    },
    {
        "clave": "consumo_automovil_diesel_l_por_km",
        "valor": "0.065",
        "tipo": "float",
        "descripcion": "Consumo automóvil diésel (litros/km)",
    },
    {
        "clave": "consumo_automovil_gas_m3_por_km",
        "valor": "0.10",
        "tipo": "float",
        "descripcion": "Consumo automóvil gas (m³/km)",
    },
    {
        "clave": "consumo_moto_gasolina_l_por_km",
        "valor": "0.03",
        "tipo": "float",
        "descripcion": "Consumo moto gasolina (litros/km)",
    },
    {
        "clave": "tarifa_base_automovil_bs",
        "valor": "3.00",
        "tipo": "float",
        "descripcion": "Tarifa mínima por viaje en automóvil (Bs)",
    },
    {
        "clave": "tarifa_base_moto_bs",
        "valor": "2.00",
        "tipo": "float",
        "descripcion": "Tarifa mínima por viaje en moto (Bs)",
    },
    {
        "clave": "comision_app_porcentaje",
        "valor": "15.0",
        "tipo": "float",
        "descripcion": "Porcentaje que cobra la app por viaje",
    },
    {
        "clave": "tipo_cambio_bs_usd",
        "valor": "6.86",
        "tipo": "float",
        "descripcion": "Tipo de cambio boliviano a dólar",
    },
    {
        "clave": "radio_maximo_caminata_m",
        "valor": "800",
        "tipo": "int",
        "descripcion": "Radio máximo de caminata al punto de abordaje (metros)",
    },
    {
        "clave": "limite_rutas_pasajero",
        "valor": "10",
        "tipo": "int",
        "descripcion": "Cantidad máxima de rutas a mostrar al pasajero",
    },
    {
        "clave": "meses_morosidad_congelamiento",
        "valor": "2",
        "tipo": "int",
        "descripcion": "Meses sin pagar comisiones para congelar cuenta del conductor",
    },
    {
        "clave": "penalizacion_cancelacion_porcentaje",
        "valor": "10.0",
        "tipo": "float",
        "descripcion": "Porcentaje del viaje cobrado como penalización por cancelar",
    },
]


@router.get("/")
async def obtener_configuraciones(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ConfiguracionGlobal))
    configs = result.scalars().all()

    response = {}
    for c in configs:
        val = c.valor
        if c.tipo == "float":
            val = float(c.valor)
        elif c.tipo == "int":
            val = int(c.valor)
        response[c.clave] = {"valor": val, "tipo": c.tipo, "descripcion": c.descripcion}
    return response


@router.put("/{clave}")
async def actualizar_configuracion(
    clave: str,
    req: ActualizarConfiguracionRequest,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ConfiguracionGlobal).where(ConfiguracionGlobal.clave == clave)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=404, detail="La variable de configuración no existe"
        )

    # Validar el tipo de dato
    try:
        if config.tipo == "float":
            float(req.valor)
        elif config.tipo == "int":
            int(req.valor)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El valor proporcionado no coincide con el tipo esperado: {config.tipo}",
        )

    config.valor = req.valor
    config.actualizado_por = current_user.id

    await db.commit()
    return {
        "mensaje": f"Configuración {clave} actualizada correctamente",
        "nuevo_valor": req.valor,
    }


@router.post("/reset")
async def restaurar_configuraciones(
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    # Eliminar configuraciones existentes
    await db.execute(select(ConfiguracionGlobal))
    # Por simplicidad, actualizamos o insertamos los iniciales
    for c_init in CONFIGURACION_INICIAL:
        result = await db.execute(
            select(ConfiguracionGlobal).where(
                ConfiguracionGlobal.clave == c_init["clave"]
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.valor = c_init["valor"]
            existing.actualizado_por = current_user.id
        else:
            new_c = ConfiguracionGlobal(
                clave=c_init["clave"],
                valor=c_init["valor"],
                tipo=c_init["tipo"],
                descripcion=c_init["descripcion"],
                actualizado_por=current_user.id,
            )
            db.add(new_c)

    await db.commit()
    return {"mensaje": "Configuraciones globales restauradas a los valores por defecto"}
