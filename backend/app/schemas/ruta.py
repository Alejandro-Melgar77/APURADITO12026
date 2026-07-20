from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class Coordenada(BaseModel):
    lon: float
    lat: float


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
    linea_ruta_coor: List[Coordenada]  # Lista de puntos para armar la LINESTRING


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
    radio_max_m: Optional[float] = None
    limite: Optional[int] = None
