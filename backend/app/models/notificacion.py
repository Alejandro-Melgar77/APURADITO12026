import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    titulo = Column(String(255), nullable=False)
    mensaje = Column(String, nullable=False)
    tipo = Column(
        String(30), nullable=False
    )  # 'solicitud_viaje','pago','calificacion','sistema','simulacion'
    leida = Column(Boolean, default=False)
    data_extra = Column(JSONB, nullable=True)
    creado_en = Column(DateTime, default=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="notificaciones")
