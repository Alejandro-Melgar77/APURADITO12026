import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conductor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conductores.id", ondelete="CASCADE"),
        nullable=False,
    )
    placa = Column(String(20), unique=True, nullable=False, index=True)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    color = Column(String(30), nullable=False)
    anio = Column(Integer, nullable=False)
    tipo = Column(String(20), nullable=False)  # 'automovil' o 'moto'
    combustible = Column(String(20), nullable=False)  # 'gasolina', 'diesel', 'gas'
    asientos_totales = Column(Integer, nullable=False)
    foto_placa_url = Column(String, nullable=True)
    placa_detectada_ia = Column(String(20), nullable=True)
    placa_verificada = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=func.now())

    # Relaciones
    conductor = relationship("Conductor", back_populates="vehiculos")
    rutas_publicadas = relationship("RutaPublicada", back_populates="vehiculo")
