import uuid
import io
import base64
import json
import qrcode
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_active_user
from app.models.usuario import Usuario
from app.models.recarga_coins import RecargaCoins
from app.models.notificacion import Notificacion
from app.models.conductor import Conductor

router = APIRouter()


class IniciarRecargaRequest(BaseModel):
    monto_bs: float = Field(..., gt=0, description="Monto en Bolivianos a recargar")


class ConfirmarRecargaRequest(BaseModel):
    referencia: str


class SolicitarRetiroRequest(BaseModel):
    monto_coins: float = Field(..., gt=0, description="Monto de Coins a retirar")


def generar_qr_base64(data: dict) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(data))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


@router.post("/iniciar-recarga")
async def iniciar_recarga(
    req: IniciarRecargaRequest,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Generar referencia única
    user_id_hex = str(current_user.id).replace("-", "")[:8].upper()
    referencia = f"APU-{user_id_hex}-{uuid.uuid4().hex[:12].upper()}"

    # Datos para el código QR
    qr_payload = {
        "app": "Apuradito",
        "cuenta": "Apuradito Carpooling S.A.",
        "monto_bs": req.monto_bs,
        "referencia": referencia,
        "instrucciones": "Transfiera el monto indicado a la cuenta de la empresa usando esta referencia como concepto de pago.",
    }

    qr_base64 = generar_qr_base64(qr_payload)

    # Crear registro de recarga pendiente
    nueva_recarga = RecargaCoins(
        usuario_id=current_user.id,
        monto_bs=req.monto_bs,
        coins_acreditados=req.monto_bs,  # 1 Bs = 1 Coin
        referencia_unica=referencia,
        qr_data=qr_base64,
        estado="pendiente",
        verificacion_automatica=True,
    )

    db.add(nueva_recarga)
    await db.commit()

    return {
        "recarga_id": str(nueva_recarga.id),
        "referencia": referencia,
        "monto_bs": req.monto_bs,
        "qr_base64": qr_base64,
        "instrucciones": "Realice la transferencia bancaria y presione confirmar para verificar automáticamente.",
    }


@router.post("/confirmar-recarga")
async def confirmar_recarga(
    req: ConfirmarRecargaRequest,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Las recargas deben confirmarse mediante un webhook del proveedor de pagos en produccion",
        )
    # Buscar recarga por referencia
    result = await db.execute(
        select(RecargaCoins).where(
            RecargaCoins.referencia_unica == req.referencia.strip().upper(),
            RecargaCoins.usuario_id == current_user.id,
        )
    )
    recarga = result.scalar_one_or_none()

    if not recarga:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La referencia de recarga no existe",
        )

    if recarga.estado != "pendiente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Esta recarga ya se encuentra en estado: {recarga.estado}",
        )

    # Actualizar estado a confirmado (automatización simulada)
    recarga.estado = "confirmado"

    # Sumar coins al usuario
    current_user.saldo_coins = float(current_user.saldo_coins or 0) + float(
        recarga.coins_acreditados
    )

    # Generar notificación
    notificacion = Notificacion(
        usuario_id=current_user.id,
        titulo="Recarga Exitosa",
        mensaje=f"Se han acreditado {recarga.coins_acreditados} Coins a tu saldo. ¡Gracias por usar Apuradito!",
        tipo="pago",
        leida=False,
    )
    db.add(notificacion)

    await db.commit()
    await db.refresh(current_user)

    return {
        "mensaje": f"Recarga de {recarga.coins_acreditados} Coins confirmada exitosamente.",
        "saldo_actual": float(current_user.saldo_coins),
    }


@router.get("/saldo")
async def obtener_saldo(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RecargaCoins)
        .where(RecargaCoins.usuario_id == current_user.id)
        .order_by(RecargaCoins.creado_en.desc())
    )
    historial = result.scalars().all()

    historial_list = []
    for h in historial:
        historial_list.append(
            {
                "id": str(h.id),
                "monto_bs": float(h.monto_bs),
                "coins": float(h.coins_acreditados),
                "referencia": h.referencia_unica,
                "estado": h.estado,
                "creado_en": h.creado_en.isoformat(),
            }
        )

    return {
        "saldo_coins": float(current_user.saldo_coins or 0),
        "historial": historial_list,
    }


@router.post("/solicitar-retiro")
async def solicitar_retiro(
    req: SolicitarRetiroRequest,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Validar que el usuario sea conductor
    if current_user.rol not in ["conductor", "ambos"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los conductores registrados pueden solicitar retiros",
        )

    # Verificar si el conductor está congelado
    result_cond = await db.execute(
        select(Conductor).where(Conductor.usuario_id == current_user.id)
    )
    conductor = result_cond.scalar_one_or_none()
    if not conductor or conductor.cuenta_congelada:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta de conductor está temporalmente congelada por morosidad de comisiones.",
        )

    # Verificar saldo suficiente
    if float(current_user.saldo_coins or 0) < req.monto_coins:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo de Coins insuficiente para procesar el retiro solicitado",
        )

    # Restar saldo de coins al usuario de forma inmediata (retención)
    current_user.saldo_coins = float(current_user.saldo_coins) - req.monto_coins

    # Crear una recarga negativa en el historial para control
    nuevo_retiro = RecargaCoins(
        usuario_id=current_user.id,
        monto_bs=-req.monto_coins,
        coins_acreditados=-req.monto_coins,
        referencia_unica=f"RET-{str(current_user.id).replace('-', '')[:8].upper()}-{uuid.uuid4().hex[:12].upper()}",
        estado="pendiente",
        verificacion_automatica=False,  # Requiere que el admin le transfiera dinero real y apruebe
    )
    db.add(nuevo_retiro)

    # Notificación de solicitud de retiro registrada
    notificacion = Notificacion(
        usuario_id=current_user.id,
        titulo="Retiro Solicitado",
        mensaje=f"Tu solicitud de retiro de {req.monto_coins} Coins ha sido recibida y está en proceso de verificación por la administración.",
        tipo="pago",
        leida=False,
    )
    db.add(notificacion)

    await db.commit()

    return {
        "mensaje": "Solicitud de retiro registrada. El administrador realizará la transferencia bancaria en las próximas 48 horas.",
        "monto_retirado": req.monto_coins,
        "saldo_restante": float(current_user.saldo_coins),
    }
