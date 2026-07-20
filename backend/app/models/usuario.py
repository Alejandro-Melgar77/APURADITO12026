import uuid
from sqlalchemy import Column, String, Date, Boolean, Numeric, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    ci_carnet = Column(String(20), unique=True, nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    telefono = Column(String(20), nullable=True)
    foto_perfil_url = Column(String, nullable=True)
    foto_facial_verificacion_url = Column(String, nullable=True)
    rol = Column(
        String(20), nullable=False, default="pasajero"
    )  # 'conductor','pasajero','ambos','admin'
    estado = Column(
        String(20), nullable=False, default="pendiente"
    )  # 'pendiente','activo','suspendido','eliminado'
    verificado_facial = Column(Boolean, default=False)
    google_uid = Column(String(255), unique=True, nullable=True)
    saldo_coins = Column(Numeric(10, 2), default=0.00)
    creado_en = Column(DateTime, default=func.now())
    actualizado_en = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relaciones
    conductor = relationship(
        "Conductor",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )
    consentimientos = relationship("ConsentimientoUsuario", back_populates="usuario")
    reclamos = relationship("Reclamo", back_populates="usuario")
    notificaciones = relationship("Notificacion", back_populates="usuario")
    recargas = relationship(
        "RecargaCoins",
        foreign_keys="RecargaCoins.usuario_id",
        back_populates="usuario",
    )
