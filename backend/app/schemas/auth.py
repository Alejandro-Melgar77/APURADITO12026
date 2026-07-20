from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date
from app.schemas.usuario import UsuarioResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class RegistroPasajeroRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    nombre: str = Field(..., max_length=100)
    apellido: str = Field(..., max_length=100)
    ci_carnet: Optional[str] = Field(None, max_length=20)
    fecha_nacimiento: Optional[date] = None
    telefono: Optional[str] = Field(None, max_length=20)


class RegistroConductorRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    nombre: str = Field(..., max_length=100)
    apellido: str = Field(..., max_length=100)
    ci_carnet: str = Field(..., max_length=20)
    fecha_nacimiento: date
    telefono: str = Field(..., max_length=20)

    # Datos de su primer vehículo
    placa: str = Field(..., max_length=20)
    marca: str = Field(..., max_length=50)
    modelo: str = Field(..., max_length=50)
    color: str = Field(..., max_length=30)
    anio: int
    tipo: str = "automovil"  # 'automovil' o 'moto'
    combustible: str = "gasolina"  # 'gasolina', 'diesel', 'gas'
    asientos_totales: int
