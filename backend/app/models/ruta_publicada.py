import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from app.core.database import Base


class RutaPublicada(Base):
    __tablename__ = "rutas_publicadas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conductor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conductores.id", ondelete="CASCADE"),
        nullable=False,
    )
    vehiculo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehiculos.id", ondelete="SET NULL"),
        nullable=True,
    )

    # PostGIS Geographies
    origen_punto = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    origen_direccion = Column(String(255), nullable=True)
    destino_punto = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    destino_direccion = Column(String(255), nullable=True)
    linea_ruta = Column(Geography(geometry_type="LINESTRING", srid=4326), nullable=True)

    distancia_total_km = Column(Numeric(8, 2), nullable=True)
    duracion_estimada_min = Column(Integer, nullable=True)
    asientos_disponibles = Column(Integer, nullable=False)
    estado = Column(
        String(20), nullable=False, default="programada"
    )  # 'programada', 'en_curso', 'completada', 'cancelada'
    hora_salida = Column(DateTime, nullable=False)
    hora_llegada_estimada = Column(DateTime, nullable=True)
    guardar_recorrido = Column(Boolean, default=False)
    recorrido_real = Column(
        Geography(geometry_type="LINESTRING", srid=4326), nullable=True
    )
    es_simulacion = Column(Boolean, default=False)
    creado_en = Column(DateTime, default=func.now())

    # Relaciones
    conductor = relationship("Conductor", back_populates="rutas_publicadas")
    vehiculo = relationship("Vehiculo", back_populates="rutas_publicadas")
    solicitudes = relationship(
        "SolicitudViaje", back_populates="ruta_publicada", cascade="all, delete-orphan"
    )
    bitacoras = relationship(
        "BitacoraRecorrido",
        back_populates="ruta_publicada",
        cascade="all, delete-orphan",
    )
