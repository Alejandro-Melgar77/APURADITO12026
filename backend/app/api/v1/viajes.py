from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.usuario import Usuario
from app.models.conductor import Conductor
from app.models.ruta_publicada import RutaPublicada
from app.models.solicitud_viaje import SolicitudViaje
from app.models.pago import Pago
from app.models.calificacion import Calificacion
from app.models.notificacion import Notificacion
from app.schemas.viaje import (
    SolicitudViajeCreate,
    SolicitudViajeResponse,
    CalificarRequest,
)
from app.services.calculo_precio import calcular_penalizacion, obtener_config
from datetime import datetime

router = APIRouter()


@router.post(
    "/solicitar",
    response_model=SolicitudViajeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def solicitar_viaje(
    req: SolicitudViajeCreate,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Validar que no se solicite a sí mismo
    res_ruta = await db.execute(
        select(RutaPublicada).where(RutaPublicada.id == req.ruta_publicada_id)
    )
    ruta = res_ruta.scalar_one_or_none()

    if not ruta:
        raise HTTPException(status_code=404, detail="La ruta publicada no existe")

    res_cond = await db.execute(
        select(Conductor).where(Conductor.id == ruta.conductor_id)
    )
    conductor = res_cond.scalar_one_or_none()

    if conductor and conductor.usuario_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes solicitar unirte a tu propia ruta publicada",
        )

    if ruta.asientos_disponibles <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No quedan asientos disponibles en este viaje",
        )

    # Formatear PostGIS POINTs
    pto_abordaje_wkt = (
        f"SRID=4326;POINT({req.punto_abordaje.lon} {req.punto_abordaje.lat})"
    )
    pto_desabordaje_wkt = (
        f"SRID=4326;POINT({req.punto_desabordaje.lon} {req.punto_desabordaje.lat})"
    )

    destino_final_wkt = None
    if req.destino_final_pasajero:
        destino_final_wkt = f"SRID=4326;POINT({req.destino_final_pasajero.lon} {req.destino_final_pasajero.lat})"

    # Validar saldo si paga con coins
    if req.metodo_pago == "coins":
        if float(current_user.saldo_coins or 0) < req.costo_calculado_bs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Saldo de Coins insuficiente ({current_user.saldo_coins} Coins) para el costo estimado de {req.costo_calculado_bs} Bs.",
            )

    # Crear la solicitud
    nueva_solicitud = SolicitudViaje(
        pasajero_id=current_user.id,
        ruta_publicada_id=req.ruta_publicada_id,
        punto_abordaje=pto_abordaje_wkt,
        punto_desabordaje=pto_desabordaje_wkt,
        destino_final_pasajero=destino_final_wkt,
        distancia_caminata_abordaje_m=req.distancia_caminata_abordaje_m,
        distancia_caminata_desabordaje_m=req.distancia_caminata_desabordaje_m,
        distancia_viaje_km=req.distancia_viaje_km,
        costo_calculado_bs=req.costo_calculado_bs,
        estado="pendiente",
        metodo_pago=req.metodo_pago,
    )

    db.add(nueva_solicitud)

    # Notificar al conductor
    notif = Notificacion(
        usuario_id=conductor.usuario_id,
        titulo="Nueva solicitud de viaje",
        mensaje=f"El pasajero {current_user.nombre} {current_user.apellido} solicita unirse a tu ruta por un valor de {req.costo_calculado_bs} Bs.",
        tipo="solicitud_viaje",
        leida=False,
    )
    db.add(notif)

    await db.commit()
    await db.refresh(nueva_solicitud)
    return nueva_solicitud


@router.post("/{id}/aceptar", response_model=SolicitudViajeResponse)
async def aceptar_solicitud(
    id: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Buscar solicitud
    result = await db.execute(select(SolicitudViaje).where(SolicitudViaje.id == id))
    solicitud = result.scalar_one_or_none()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud de viaje no encontrada")

    if solicitud.estado != "pendiente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La solicitud ya no está pendiente (estado actual: {solicitud.estado})",
        )

    # Validar que pertenezca al conductor actual
    res_ruta = await db.execute(
        select(RutaPublicada).where(RutaPublicada.id == solicitud.ruta_publicada_id)
    )
    ruta = res_ruta.scalar_one_or_none()

    res_cond = await db.execute(
        select(Conductor).where(Conductor.id == ruta.conductor_id)
    )
    conductor = res_cond.scalar_one_or_none()

    if not conductor or conductor.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes autorización para aceptar esta solicitud",
        )

    if ruta.asientos_disponibles <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay más asientos disponibles en tu vehículo",
        )

    # Actualizar estado de la solicitud y descontar asiento
    solicitud.estado = "aceptada"
    ruta.asientos_disponibles -= 1

    # Notificar al pasajero
    notif = Notificacion(
        usuario_id=solicitud.pasajero_id,
        titulo="Solicitud Aceptada",
        mensaje=f"El conductor {current_user.nombre} ha aceptado tu solicitud de viaje. Prepárate para el abordaje.",
        tipo="solicitud_viaje",
        leida=False,
    )
    db.add(notif)

    await db.commit()
    await db.refresh(solicitud)
    return solicitud


@router.post("/{id}/rechazar", response_model=SolicitudViajeResponse)
async def rechazar_solicitud(
    id: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SolicitudViaje).where(SolicitudViaje.id == id))
    solicitud = result.scalar_one_or_none()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud de viaje no encontrada")

    if solicitud.estado != "pendiente":
        raise HTTPException(status_code=400, detail="La solicitud no está pendiente")

    res_ruta = await db.execute(
        select(RutaPublicada).where(RutaPublicada.id == solicitud.ruta_publicada_id)
    )
    ruta = res_ruta.scalar_one_or_none()

    if ruta.conductor.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="Operación no autorizada")

    solicitud.estado = "rechazada"

    # Notificar al pasajero
    notif = Notificacion(
        usuario_id=solicitud.pasajero_id,
        titulo="Solicitud Rechazada",
        mensaje="El conductor ha rechazado tu solicitud de viaje.",
        tipo="solicitud_viaje",
        leida=False,
    )
    db.add(notif)

    await db.commit()
    await db.refresh(solicitud)
    return solicitud


@router.post("/{id}/cancelar", response_model=SolicitudViajeResponse)
async def cancelar_viaje(
    id: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SolicitudViaje).where(SolicitudViaje.id == id))
    solicitud = result.scalar_one_or_none()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud de viaje no encontrada")

    if solicitud.estado not in ["pendiente", "aceptada"]:
        raise HTTPException(
            status_code=400, detail="No se puede cancelar en el estado actual"
        )

    res_ruta = await db.execute(
        select(RutaPublicada).where(RutaPublicada.id == solicitud.ruta_publicada_id)
    )
    ruta = res_ruta.scalar_one_or_none()

    es_pasajero = solicitud.pasajero_id == current_user.id
    es_conductor = ruta.conductor.usuario_id == current_user.id

    if not es_pasajero and not es_conductor:
        raise HTTPException(status_code=403, detail="Operación no autorizada")

    estado_anterior = solicitud.estado
    solicitud.estado = "cancelada"
    solicitud.cancelado_por = "pasajero" if es_pasajero else "conductor"

    # Si estaba aceptada, devolvemos el asiento a la ruta
    if estado_anterior == "aceptada":
        ruta.asientos_disponibles += 1

        # Aplicar penalización del 10% del viaje
        penalizacion = await calcular_penalizacion(
            float(solicitud.costo_calculado_bs), db
        )
        solicitud.penalizacion_aplicada = True
        solicitud.penalizacion_bs = penalizacion

        # Descontar de coins al cancelador
        if es_pasajero:
            current_user.saldo_coins = (
                float(current_user.saldo_coins or 0) - penalizacion
            )
            # Notificar al conductor
            notif = Notificacion(
                usuario_id=ruta.conductor.usuario_id,
                titulo="Viaje Cancelado por Pasajero",
                mensaje="El pasajero canceló el viaje aceptado. Se le aplicó una penalización.",
                tipo="solicitud_viaje",
                leida=False,
            )
            db.add(notif)
        else:
            # El conductor cancela, descontamos del saldo del conductor de su cuenta de usuario
            conductor_user = ruta.conductor.usuario
            conductor_user.saldo_coins = (
                float(conductor_user.saldo_coins or 0) - penalizacion
            )
            # Notificar al pasajero
            notif = Notificacion(
                usuario_id=solicitud.pasajero_id,
                titulo="Viaje Cancelado por Conductor",
                mensaje="El conductor canceló el viaje. Te pedimos disculpas.",
                tipo="solicitud_viaje",
                leida=False,
            )
            db.add(notif)

    await db.commit()
    await db.refresh(solicitud)
    return solicitud


@router.post("/{id}/completar")
async def completar_viaje(
    id: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SolicitudViaje).where(SolicitudViaje.id == id))
    solicitud = result.scalar_one_or_none()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud de viaje no encontrada")

    if solicitud.estado != "aceptada":
        raise HTTPException(
            status_code=400,
            detail="El viaje debe estar en estado 'aceptada' para completarlo",
        )

    res_ruta = await db.execute(
        select(RutaPublicada).where(RutaPublicada.id == solicitud.ruta_publicada_id)
    )
    ruta = res_ruta.scalar_one_or_none()

    # Validar que sea completado por el conductor
    if ruta.conductor.usuario_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Solo el conductor puede marcar el viaje como completado",
        )

    solicitud.estado = "completada"

    # Calcular costos finales usando la configuración
    config = await obtener_config(db)
    comision_porc = float(config.get("comision_app_porcentaje", 15.0))

    monto_total = float(solicitud.costo_calculado_bs)
    comision_app = round(monto_total * (comision_porc / 100), 2)
    monto_neto = round(monto_total - comision_app, 2)

    # Cargar modelos de usuarios correspondientes
    res_pas = await db.execute(
        select(Usuario).where(Usuario.id == solicitud.pasajero_id)
    )
    pasajero = res_pas.scalar_one()

    conductor = ruta.conductor
    conductor_user = conductor.usuario

    # Procesamiento del pago según el método elegido
    if solicitud.metodo_pago == "coins":
        # Validar saldo del pasajero
        if float(pasajero.saldo_coins or 0) < monto_total:
            # Si no tiene suficiente saldo al final, forzamos cobro o pasamos a deuda (por simplicidad, asumimos que se debita)
            pass

        pasajero.saldo_coins = float(pasajero.saldo_coins or 0) - monto_total
        conductor_user.saldo_coins = float(conductor_user.saldo_coins or 0) + monto_neto

        # Guardar registro en la tabla de pagos
        nuevo_pago = Pago(
            solicitud_viaje_id=solicitud.id,
            pagador_id=pasajero.id,
            receptor_id=conductor_user.id,
            monto_total_bs=monto_total,
            monto_comision_app_bs=comision_app,
            monto_neto_conductor_bs=monto_neto,
            estado="completado",
            metodo="coins",
        )
        db.add(nuevo_pago)

    elif solicitud.metodo_pago == "efectivo":
        # El pasajero le paga físicamente al conductor, por lo que el saldo del conductor no se incrementa con coins.
        # En cambio, el conductor acumula una deuda de comisiones con la app.
        conductor.comisiones_pendientes_bs = (
            float(conductor.comisiones_pendientes_bs or 0) + comision_app
        )

        # Si es la primera comisión impaga, guardamos la fecha de inicio de la deuda para la morosidad
        if not conductor.fecha_inicio_deuda:
            conductor.fecha_inicio_deuda = datetime.now()

        nuevo_pago = Pago(
            solicitud_viaje_id=solicitud.id,
            pagador_id=pasajero.id,
            receptor_id=conductor_user.id,
            monto_total_bs=monto_total,
            monto_comision_app_bs=comision_app,
            monto_neto_conductor_bs=monto_neto,
            estado="completado",
            metodo="efectivo",
        )
        db.add(nuevo_pago)

    # Actualizar estadísticas del conductor
    conductor.total_viajes += 1
    conductor.km_totales = float(conductor.km_totales or 0) + float(
        solicitud.distancia_viaje_km or 0
    )

    # Notificar al pasajero que el viaje finalizó
    notif = Notificacion(
        usuario_id=pasajero.id,
        titulo="Viaje Completado",
        mensaje=f"Tu viaje con {current_user.nombre} ha finalizado. Califica tu experiencia.",
        tipo="calificacion",
        leida=False,
    )
    db.add(notif)

    await db.commit()

    return {
        "mensaje": "Viaje completado y transacciones de pago registradas con éxito.",
        "monto_total": monto_total,
        "comision_app": comision_app,
        "ganancia_conductor": monto_neto,
        "metodo_pago": solicitud.metodo_pago,
    }


@router.post("/{id}/calificar")
async def calificar_viaje(
    id: str,
    req: CalificarRequest,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(SolicitudViaje).where(SolicitudViaje.id == id))
    solicitud = result.scalar_one_or_none()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud de viaje no encontrada")

    if solicitud.estado != "completada":
        raise HTTPException(
            status_code=400, detail="Solo se pueden calificar viajes completados"
        )

    # Verificar que el calificador ya no haya calificado este viaje
    res_existente = await db.execute(
        select(Calificacion).where(
            and_(
                Calificacion.solicitud_viaje_id == solicitud.id,
                Calificacion.calificador_id == current_user.id,
            )
        )
    )
    if res_existente.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ya has calificado este viaje")

    # Registrar calificación
    nueva_calif = Calificacion(
        solicitud_viaje_id=solicitud.id,
        calificador_id=current_user.id,
        calificado_id=req.calificado_id,
        estrellas=req.estrellas,
        comentario=req.comentario,
    )
    db.add(nueva_calif)
    await db.flush()

    # Recalcular el promedio de estrellas del calificado si es conductor
    res_cond = await db.execute(
        select(Conductor).where(Conductor.usuario_id == req.calificado_id)
    )
    conductor = res_cond.scalar_one_or_none()

    if conductor:
        # Calcular promedio
        res_prom = await db.execute(
            select(func.avg(Calificacion.estrellas)).where(
                Calificacion.calificado_id == req.calificado_id
            )
        )
        promedio = res_prom.scalar() or 0.0
        conductor.calificacion_promedio = round(float(promedio), 2)

    await db.commit()
    return {"mensaje": "Calificación registrada exitosamente"}
