"""
Modelos SQLAlchemy para Rutas Publicadas, Solicitudes de Viaje,
Recargas de Coins y Solicitudes de Retiro de Apuradito.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    Numeric,
    Integer,
    ForeignKey,
    Enum as SAEnum,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry  # Para almacenar geometrías PostGIS

from app.models.configuracion_global import Base


class RutaPublicada(Base):
    """
    Ruta publicada por un conductor.
    El campo linea_ruta almacena la geometría LINESTRING en PostGIS (SRID 4326).
    """

    __tablename__ = "rutas_publicadas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conductor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conductores.id", ondelete="CASCADE"),
        nullable=False,
    )
    vehiculo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehiculos.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Origen y destino (texto descriptivo)
    origen_direccion = Column(String(300), nullable=False)
    destino_direccion = Column(String(300), nullable=False)

    # Coordenadas origen/destino (para referencia rápida)
    lon_origen = Column(Numeric(10, 7), nullable=False)
    lat_origen = Column(Numeric(10, 7), nullable=False)
    lon_destino = Column(Numeric(10, 7), nullable=False)
    lat_destino = Column(Numeric(10, 7), nullable=False)

    # Geometría de la ruta completa (PostGIS LINESTRING)
    linea_ruta = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=True)

    # Distancia total calculada en km
    distancia_total_km = Column(Numeric(10, 3), nullable=True)

    # Configuración del viaje
    asientos_disponibles = Column(Integer, nullable=False, default=1)
    asientos_totales = Column(Integer, nullable=False, default=1)
    hora_salida = Column(DateTime, nullable=False)
    precio_sugerido_bs = Column(Numeric(10, 2), nullable=True)

    # Estado de la ruta
    estado = Column(
        SAEnum("programada", "en_curso", "completada", "cancelada", name="estado_ruta"),
        nullable=False,
        default="programada",
    )

    # Modo simulación (para pruebas, no aparece en búsquedas reales)
    es_simulacion = Column(Boolean, default=False, nullable=False)

    # Puntos de parada opcionales (GeoJSON)
    paradas_json = Column(JSON, nullable=True)

    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    conductor = relationship("Conductor", back_populates="rutas_publicadas")
    vehiculo = relationship("Vehiculo", back_populates="rutas_publicadas")
    solicitudes = relationship("SolicitudViaje", back_populates="ruta_publicada")

    def __repr__(self) -> str:
        return f"<RutaPublicada id={self.id} estado={self.estado}>"


class SolicitudViaje(Base):
    """
    Solicitud de un pasajero para unirse a una ruta publicada.
    """

    __tablename__ = "solicitudes_viaje"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ruta_publicada_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rutas_publicadas.id", ondelete="CASCADE"),
        nullable=False,
    )
    pasajero_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Puntos de abordaje y desabordaje del pasajero
    lon_abordaje = Column(Numeric(10, 7), nullable=False)
    lat_abordaje = Column(Numeric(10, 7), nullable=False)
    lon_desabordaje = Column(Numeric(10, 7), nullable=False)
    lat_desabordaje = Column(Numeric(10, 7), nullable=False)

    # Destino final del pasajero
    lon_destino = Column(Numeric(10, 7), nullable=False)
    lat_destino = Column(Numeric(10, 7), nullable=False)

    # Costos calculados
    distancia_viaje_km = Column(Numeric(10, 3), nullable=False)
    costo_total_bs = Column(Numeric(10, 2), nullable=False)
    comision_app_bs = Column(Numeric(10, 2), nullable=False)
    ganancia_conductor_bs = Column(Numeric(10, 2), nullable=False)

    # Método de pago
    metodo_pago = Column(
        SAEnum("coins", "efectivo", name="metodo_pago_viaje"),
        nullable=False,
        default="efectivo",
    )

    # Estado de la solicitud
    estado = Column(
        SAEnum(
            "pendiente",
            "aceptada",
            "rechazada",
            "cancelada",
            "completada",
            name="estado_solicitud",
        ),
        nullable=False,
        default="pendiente",
    )

    # Penalización por cancelación
    penalizacion_bs = Column(Numeric(10, 2), nullable=True)
    cancelado_por = Column(
        SAEnum("pasajero", "conductor", name="quien_cancelo"), nullable=True
    )

    # Calificaciones
    calificacion_pasajero_a_conductor = Column(Integer, nullable=True)  # 1-5
    calificacion_conductor_a_pasajero = Column(Integer, nullable=True)  # 1-5
    comentario_pasajero = Column(Text, nullable=True)
    comentario_conductor = Column(Text, nullable=True)

    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    ruta_publicada = relationship("RutaPublicada", back_populates="solicitudes")
    pasajero = relationship(
        "Usuario", back_populates="solicitudes_viaje", foreign_keys=[pasajero_id]
    )

    def __repr__(self) -> str:
        return f"<SolicitudViaje id={self.id} estado={self.estado}>"


class RecargaCoins(Base):
    """
    Registro de recarga de coins de un usuario.
    La confirmación es simulada en desarrollo; en producción sería un webhook bancario.
    """

    __tablename__ = "recargas_coins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )

    monto_bs = Column(Numeric(12, 2), nullable=False)
    referencia = Column(String(50), unique=True, nullable=False, index=True)
    qr_base64 = Column(Text, nullable=True)

    estado = Column(
        SAEnum("pendiente", "confirmado", "rechazado", name="estado_recarga"),
        nullable=False,
        default="pendiente",
    )

    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    confirmado_en = Column(DateTime, nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="recargas_coins")

    def __repr__(self) -> str:
        return f"<RecargaCoins ref={self.referencia!r} estado={self.estado}>"


class SolicitudRetiro(Base):
    """
    Solicitud de retiro de coins (ganancias) de un conductor.
    Es procesada manualmente por el administrador.
    """

    __tablename__ = "solicitudes_retiro"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conductor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conductores.id", ondelete="CASCADE"),
        nullable=False,
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )

    monto_coins = Column(Numeric(12, 2), nullable=False)
    numero_cuenta_destino = Column(
        String(100), nullable=True
    )  # Datos bancarios del conductor
    banco_destino = Column(String(100), nullable=True)

    estado = Column(
        SAEnum("pendiente", "procesado", "rechazado", name="estado_retiro"),
        nullable=False,
        default="pendiente",
    )
    nota_admin = Column(Text, nullable=True)

    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    procesado_en = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<SolicitudRetiro id={self.id} monto={self.monto_coins} estado={self.estado}>"


class Notificacion(Base):
    """
    Notificaciones push/in-app para usuarios.
    """

    __tablename__ = "notificaciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )

    titulo = Column(String(200), nullable=False)
    cuerpo = Column(Text, nullable=False)
    tipo = Column(String(50), nullable=True)  # 'viaje', 'coins', 'sistema', etc.
    leida = Column(Boolean, default=False, nullable=False)
    datos_extra = Column(JSON, nullable=True)  # Datos adicionales para la notificación

    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Notificacion id={self.id} tipo={self.tipo}>"
