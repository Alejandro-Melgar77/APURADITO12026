import uuid
from sqlalchemy import Column, ForeignKey, Numeric, Integer, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Conductor(Base):
    __tablename__ = "conductores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    calificacion_promedio = Column(Numeric(3, 2), default=0.00)
    total_viajes = Column(Integer, default=0)
    km_totales = Column(Numeric(10, 2), default=0.00)
    comisiones_pendientes_bs = Column(Numeric(10, 2), default=0.00)
    cuenta_congelada = Column(Boolean, default=False)
    congelado_manualmente = Column(Boolean, default=False)
    fecha_inicio_deuda = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, default=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="conductor")
    vehiculos = relationship(
        "Vehiculo", back_populates="conductor", cascade="all, delete-orphan"
    )
    rutas_publicadas = relationship("RutaPublicada", back_populates="conductor")
