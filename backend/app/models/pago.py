import uuid
from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solicitud_viaje_id = Column(
        UUID(as_uuid=True),
        ForeignKey("solicitudes_viaje.id", ondelete="CASCADE"),
        nullable=False,
    )
    pagador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    receptor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )

    monto_total_bs = Column(Numeric(10, 2), nullable=False)
    monto_comision_app_bs = Column(Numeric(10, 2), nullable=False)
    monto_neto_conductor_bs = Column(Numeric(10, 2), nullable=False)

    estado = Column(
        String(20), nullable=False, default="pendiente"
    )  # 'pendiente', 'completado', 'fallido'
    metodo = Column(
        String(20), nullable=False, default="coins"
    )  # 'coins', 'efectivo', 'nfc'
    creado_en = Column(DateTime, default=func.now())

    # Relaciones
    solicitud = relationship("SolicitudViaje", back_populates="pagos")
    pagador = relationship("Usuario", foreign_keys=[pagador_id])
    receptor = relationship("Usuario", foreign_keys=[receptor_id])
