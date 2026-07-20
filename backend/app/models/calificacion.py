import uuid
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Integer,
    DateTime,
    func,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Calificacion(Base):
    __tablename__ = "calificaciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solicitud_viaje_id = Column(
        UUID(as_uuid=True),
        ForeignKey("solicitudes_viaje.id", ondelete="CASCADE"),
        nullable=False,
    )
    calificador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    calificado_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )

    estrellas = Column(Integer, nullable=False)  # 1 a 5
    comentario = Column(String, nullable=True)
    creado_en = Column(DateTime, default=func.now())

    # Relaciones
    solicitud_viaje = relationship("SolicitudViaje", back_populates="calificaciones")
    calificador = relationship("Usuario", foreign_keys=[calificador_id])
    calificado = relationship("Usuario", foreign_keys=[calificado_id])

    __table_args__ = (
        UniqueConstraint(
            "solicitud_viaje_id",
            "calificador_id",
            name="uq_calificacion_viaje_calificador",
        ),
    )
