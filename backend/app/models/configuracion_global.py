import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class ConfiguracionGlobal(Base):
    __tablename__ = "configuracion_global"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clave = Column(String(100), unique=True, nullable=False, index=True)
    valor = Column(String, nullable=False)
    tipo = Column(String(20), nullable=False)  # 'float', 'int', 'string', 'json'
    descripcion = Column(String, nullable=True)
    actualizado_en = Column(DateTime, default=func.now(), onupdate=func.now())
    actualizado_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relaciones
    actualizado_por_rel = relationship("Usuario", foreign_keys=[actualizado_por])
