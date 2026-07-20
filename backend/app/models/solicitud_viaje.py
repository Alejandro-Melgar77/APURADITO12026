import uuid
from sqlalchemy import Column, String, ForeignKey, Numeric, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from app.core.database import Base


class SolicitudViaje(Base):
    __tablename__ = "solicitudes_viaje"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pasajero_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    ruta_publicada_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rutas_publicadas.id", ondelete="CASCADE"),
        nullable=False,
    )

    # PostGIS Geographies para el matching exacto
    punto_abordaje = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    punto_desabordaje = Column(
        Geography(geometry_type="POINT", srid=4326), nullable=False
    )
    destino_final_pasajero = Column(
        Geography(geometry_type="POINT", srid=4326), nullable=True
    )

    distancia_caminata_abordaje_m = Column(Numeric(8, 2), nullable=True)
    distancia_caminata_desabordaje_m = Column(Numeric(8, 2), nullable=True)
    distancia_viaje_km = Column(Numeric(8, 2), nullable=True)
    costo_calculado_bs = Column(Numeric(10, 2), nullable=True)

    estado = Column(
        String(20), nullable=False, default="pendiente"
    )  # 'pendiente', 'aceptada', 'rechazada', 'cancelada', 'completada'
    metodo_pago = Column(
        String(20), nullable=False, default="coins"
    )  # 'coins', 'efectivo', 'nfc'
    cancelado_por = Column(String(20), nullable=True)  # 'pasajero', 'conductor'
    penalizacion_aplicada = Column(Boolean, default=False)
    penalizacion_bs = Column(Numeric(10, 2), default=0.00)
    creado_en = Column(DateTime, default=func.now())

    # Relaciones
    pasajero = relationship("Usuario", foreign_keys=[pasajero_id])
    ruta_publicada = relationship("RutaPublicada", back_populates="solicitudes")
    pagos = relationship(
        "Pago", back_populates="solicitud", cascade="all, delete-orphan"
    )
    calificaciones = relationship(
        "Calificacion", back_populates="solicitud_viaje", cascade="all, delete-orphan"
    )
    reclamos = relationship("Reclamo", back_populates="solicitud")
