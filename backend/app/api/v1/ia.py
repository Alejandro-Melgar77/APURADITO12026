"""Pasarela del backend principal hacia los servicios especializados de IA.

El API principal no carga modelos de visión ni de ML.  Eso mantiene su consumo
de memoria bajo y permite desplegar cada modelo con los recursos que necesita.
"""

import os
from typing import Any

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field


router = APIRouter()
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
REQUEST_TIMEOUT_SECONDS = 45.0


def _service_headers() -> dict[str, str]:
    token = os.getenv("AI_SERVICE_TOKEN", "").strip()
    return {"X-Internal-Token": token} if token else {}


def _service_url(*variables: str, path: str) -> str:
    """Obtiene y valida la URL de un servicio de IA configurado."""
    base_url = next((os.getenv(variable, "").strip().rstrip("/") for variable in variables if os.getenv(variable, "").strip()), "")
    if not base_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"El servicio de IA no está configurado ({' o '.join(variables)}).",
        )
    return f"{base_url}{path}"


async def _read_image(file: UploadFile) -> bytes:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Debes enviar un archivo de imagen.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="La imagen está vacía.")
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="La imagen supera el límite de 10 MB.")
    return contents


async def _post_file(url: str, file: UploadFile, contents: bytes) -> dict[str, Any]:
    files = {"file": (file.filename or "imagen", contents, file.content_type)}
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(url, files=files, headers=_service_headers())
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="El servicio de IA tardó demasiado.") from exc
    except httpx.HTTPStatusError as exc:
        detail: Any = "El servicio de IA no pudo procesar la solicitud."
        try:
            detail = exc.response.json().get("detail", detail)
        except ValueError:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar con el servicio de IA.",
        ) from exc


async def _post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(url, json=payload, headers=_service_headers())
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="El servicio de IA tardó demasiado.") from exc
    except httpx.HTTPStatusError as exc:
        detail: Any = "El servicio de IA no pudo procesar la solicitud."
        try:
            detail = exc.response.json().get("detail", detail)
        except ValueError:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=detail) from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail="No se pudo conectar con el servicio de IA.") from exc


@router.post("/facial-recognition")
async def api_facial_recognition(file: UploadFile = File(...)) -> dict[str, Any]:
    """Detecta un rostro delegando en el servicio facial especializado."""
    contents = await _read_image(file)
    result = await _post_file(_service_url("FACE_SERVICE_URL", "AI_FACIAL_URL", path="/v1/facial/detect"), file, contents)
    return {"has_face": result}


@router.post("/ocr-plates")
async def api_ocr_plates(file: UploadFile = File(...)) -> dict[str, Any]:
    """Lee una placa delegando en el servicio OCR especializado."""
    contents = await _read_image(file)
    result = await _post_file(_service_url("OCR_SERVICE_URL", "AI_OCR_URL", path="/v1/ocr/plates"), file, contents)
    return {"plate_text": result}


@router.post("/facial-verify")
async def api_facial_verify(
    reference: UploadFile = File(...), probe: UploadFile = File(...), threshold: float = 0.60
) -> dict[str, Any]:
    """Compara dos rostros mediante el servicio facial especializado."""
    reference_contents = await _read_image(reference)
    probe_contents = await _read_image(probe)
    url = _service_url("FACE_SERVICE_URL", "AI_FACIAL_URL", path="/v1/facial/verify")
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(
                url,
                params={"threshold": threshold},
                headers=_service_headers(),
                files={
                    "reference": (reference.filename or "referencia", reference_contents, reference.content_type),
                    "probe": (probe.filename or "prueba", probe_contents, probe.content_type),
                },
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="El servicio facial tardó demasiado.") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="No se pudo verificar el rostro.") from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail="No se pudo conectar con el servicio facial.") from exc


class Coordinate(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class RouteCandidate(BaseModel):
    route_id: str
    origin: Coordinate
    destination: Coordinate
    available_seats: int = Field(ge=0, le=100)
    price_bs: float = Field(ge=0, le=10_000)
    driver_rating: float = Field(default=5.0, ge=0, le=5)
    estimated_minutes: float | None = Field(default=None, ge=0, le=1_440)


class MatchingRequest(BaseModel):
    passenger_origin: Coordinate
    passenger_destination: Coordinate
    candidates: list[RouteCandidate]
    limit: int = Field(default=5, ge=1, le=25)


@router.post("/matching/routes")
async def api_match_routes(payload: MatchingRequest) -> dict[str, Any]:
    """Puntúa rutas con el servicio de optimización/aprendizaje."""
    url = _service_url("ROUTES_AI_SERVICE_URL", "AI_ROUTES_URL", path="/v1/routes/score")
    return await _post_json(url, payload.model_dump(mode="json"))


class HistoryTrip(BaseModel):
    completed_at: str
    origin: Coordinate
    destination: Coordinate
    passenger_count: int = Field(default=1, ge=1, le=20)
    completed: bool = True


class TrainingRequest(BaseModel):
    trips: list[HistoryTrip] = Field(min_length=1, max_length=100_000)


@router.post("/matching/train")
async def api_train_route_model(payload: TrainingRequest) -> dict[str, Any]:
    """Entrena el modelo de demanda con el historial autorizado de viajes."""
    url = _service_url("ROUTES_AI_SERVICE_URL", "AI_ROUTES_URL", path="/v1/routes/train")
    return await _post_json(url, payload.model_dump(mode="json"))
