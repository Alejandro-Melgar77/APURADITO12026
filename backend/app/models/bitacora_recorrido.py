import uuid
from sqlalchemy import Column, ForeignKey, Numeric, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from app.core.database import Base


class BitacoraRecorrido(Base):
    __tablename__ = "bitacora_recorrido"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ruta_publicada_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rutas_publicadas.id", ondelete="CASCADE"),
        nullable=False,
    )
    punto = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    velocidad_kmh = Column(Numeric(5, 2), nullable=True)
    registrado_en = Column(DateTime, default=func.now())

    # Relaciones
    ruta_publicada = relationship("RutaPublicada", back_populates="bitacoras")
