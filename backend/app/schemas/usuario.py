from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal


class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str = Field(..., max_length=100)
    apellido: str = Field(..., max_length=100)
    ci_carnet: Optional[str] = Field(None, max_length=20)
    fecha_nacimiento: Optional[date] = None
    telefono: Optional[str] = Field(None, max_length=20)
    rol: str = "pasajero"  # 'conductor','pasajero','ambos','admin'
    estado: str = "pendiente"  # 'pendiente','activo','suspendido','eliminado'


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)


class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    ci_carnet: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    telefono: Optional[str] = None
    foto_perfil_url: Optional[str] = None
    foto_facial_verificacion_url: Optional[str] = None
    rol: Optional[str] = None
    estado: Optional[str] = None
    verificado_facial: Optional[bool] = None
    saldo_coins: Optional[Decimal] = None


class UsuarioResponse(UsuarioBase):
    id: UUID
    foto_perfil_url: Optional[str] = None
    foto_facial_verificacion_url: Optional[str] = None
    verificado_facial: bool
    google_uid: Optional[str] = None
    saldo_coins: Decimal
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True


class UsuarioListResponse(BaseModel):
    id: UUID
    email: str
    nombre: str
    apellido: str
    rol: str
    estado: str
    verificado_facial: bool
    creado_en: datetime

    class Config:
        from_attributes = True
