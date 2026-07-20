import uuid
from sqlalchemy import Column, String, ForeignKey, Numeric, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class RecargaCoins(Base):
    __tablename__ = "recargas_coins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    monto_bs = Column(Numeric(10, 2), nullable=False)
    coins_acreditados = Column(Numeric(10, 2), nullable=False)
    referencia_unica = Column(String(50), unique=True, nullable=False, index=True)
    qr_data = Column(String, nullable=True)
    estado = Column(
        String(20), nullable=False, default="pendiente"
    )  # 'pendiente', 'confirmado', 'rechazado'
    verificacion_automatica = Column(Boolean, default=True)
    confirmado_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )
    creado_en = Column(DateTime, default=func.now())

    # Relaciones
    usuario = relationship(
        "Usuario", foreign_keys=[usuario_id], back_populates="recargas"
    )
    confirmado_por_rel = relationship("Usuario", foreign_keys=[confirmado_por])
