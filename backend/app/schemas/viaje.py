from pydantic import BaseModel, Field
from typing import Literal, Optional
from uuid import UUID
from datetime import datetime
from app.schemas.ruta import Coordenada


class SolicitudViajeCreate(BaseModel):
    ruta_publicada_id: UUID
    punto_abordaje: Coordenada
    punto_desabordaje: Coordenada
    destino_final_pasajero: Optional[Coordenada] = None
    distancia_caminata_abordaje_m: float = Field(..., ge=0)
    distancia_caminata_desabordaje_m: float = Field(..., ge=0)
    distancia_viaje_km: float = Field(..., gt=0)
    costo_calculado_bs: float = Field(..., ge=0)
    metodo_pago: Literal["coins", "efectivo"] = "coins"


class SolicitudViajeResponse(BaseModel):
    id: UUID
    pasajero_id: UUID
    ruta_publicada_id: UUID
    distancia_viaje_km: float
    costo_calculado_bs: float
    estado: str
    metodo_pago: str
    creado_en: datetime

    class Config:
        from_attributes = True


class CalificarRequest(BaseModel):
    calificado_id: UUID
    estrellas: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = None
