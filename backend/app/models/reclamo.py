import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Reclamo(Base):
    __tablename__ = "reclamos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    solicitud_viaje_id = Column(
        UUID(as_uuid=True),
        ForeignKey("solicitudes_viaje.id", ondelete="SET NULL"),
        nullable=True,
    )

    tipo = Column(String(20), nullable=False)  # 'reclamo', 'denuncia', 'sugerencia'
    asunto = Column(String(255), nullable=False)
    descripcion = Column(String, nullable=False)
    estado = Column(
        String(20), nullable=False, default="abierto"
    )  # 'abierto', 'en_revision', 'resuelto', 'cerrado'
    creado_en = Column(DateTime, default=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="reclamos")
    solicitud = relationship("SolicitudViaje", back_populates="reclamos")
