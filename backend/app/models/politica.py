import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Politica(Base):
    __tablename__ = "politicas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = Column(String(255), nullable=False)
    contenido_html = Column(String, nullable=False)
    tipo = Column(
        String(30), nullable=False
    )  # 'terminos','privacidad','consentimiento_ubicacion','consentimiento_nfc','pagos'
    version = Column(Integer, nullable=False, default=1)
    activa = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=func.now())

    # Relaciones
    consentimientos = relationship("ConsentimientoUsuario", back_populates="politica")


class ConsentimientoUsuario(Base):
    __tablename__ = "consentimientos_usuario"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    politica_id = Column(
        UUID(as_uuid=True),
        ForeignKey("politicas.id", ondelete="CASCADE"),
        nullable=False,
    )
    aceptado = Column(Boolean, nullable=False)
    aceptado_en = Column(DateTime, default=func.now())
    ip_address = Column(String(50), nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="consentimientos")
    politica = relationship("Politica", back_populates="consentimientos")
