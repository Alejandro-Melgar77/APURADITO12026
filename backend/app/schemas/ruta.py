from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class Coordenada(BaseModel):
    lon: float = Field(..., ge=-180, le=180)
    lat: float = Field(..., ge=-90, le=90)


class RutaPublicadaBase(BaseModel):
    origen_direccion: Optional[str] = None
    destino_direccion: Optional[str] = None
    distancia_total_km: Optional[float] = None
    duracion_estimada_min: Optional[int] = None
    asientos_disponibles: int = Field(..., gt=0)
    hora_salida: datetime
    guardar_recorrido: bool = False
    es_simulacion: bool = False


class RutaPublicadaCreate(RutaPublicadaBase):
    origen_coor: Coordenada
    destino_coor: Coordenada
    linea_ruta_coor: List[Coordenada] = Field(..., min_length=2)


class RutaPublicadaResponse(RutaPublicadaBase):
    id: UUID
    conductor_id: UUID
    vehiculo_id: Optional[UUID] = None
    estado: str
    creado_en: datetime

    class Config:
        from_attributes = True


class BuscarRutaRequest(BaseModel):
    lon_pasajero: float
    lat_pasajero: float
    lon_destino: float
    lat_destino: float
    radio_max_m: Optional[float] = Field(None, gt=0, le=10_000)
    limite: Optional[int] = Field(None, ge=1, le=50)
