import logging
import os
import secrets
import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


class FaceDetection(BaseModel):
    detected: bool
    count: int
    engine: str
    fallback_used: bool


class FaceVerification(BaseModel):
    match: bool
    distance: float | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    engine: str
    fallback_used: bool


def decode_image(content: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("El archivo no contiene una imagen válida.")
    return image


def haar_faces(image: np.ndarray) -> list[tuple[int, int, int, int]]:
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return list(cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48)))


def import_face_recognition():
    import face_recognition

    return face_recognition


def face_encodings(image: np.ndarray) -> list[np.ndarray]:
    module = import_face_recognition()
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return module.face_encodings(rgb)


def detect(content: bytes) -> FaceDetection:
    image = decode_image(content)
    if os.getenv("FACE_ENGINE", "face_recognition").lower() == "opencv":
        faces = haar_faces(image)
        return FaceDetection(detected=bool(faces), count=len(faces), engine="opencv_haar", fallback_used=True)
    try:
        module = import_face_recognition()
        locations = module.face_locations(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        return FaceDetection(detected=bool(locations), count=len(locations), engine="face_recognition", fallback_used=False)
    except Exception as exc:
        logger.warning("face_recognition unavailable; using Haar fallback: %s", exc)
        faces = haar_faces(image)
        return FaceDetection(detected=bool(faces), count=len(faces), engine="opencv_haar", fallback_used=True)


def verify(reference: bytes, probe: bytes, threshold: float = 0.60) -> FaceVerification:
    if os.getenv("FACE_ENGINE", "face_recognition").lower() == "opencv":
        return FaceVerification(match=False, confidence=0.0, reason="FACE_ENGINE=opencv solo permite detección, no verificación biométrica.", engine="opencv_haar", fallback_used=True)
    try:
        reference_encodings = face_encodings(decode_image(reference))
        probe_encodings = face_encodings(decode_image(probe))
        if len(reference_encodings) != 1 or len(probe_encodings) != 1:
            return FaceVerification(match=False, confidence=0.0, reason="Se requiere exactamente un rostro en cada imagen.", engine="face_recognition", fallback_used=False)
        distance = float(np.linalg.norm(reference_encodings[0] - probe_encodings[0]))
        confidence = max(0.0, min(1.0, 1.0 - (distance / threshold)))
        return FaceVerification(match=distance <= threshold, distance=distance, confidence=confidence, reason="Comparación biométrica completada.", engine="face_recognition", fallback_used=False)
    except (ImportError, ModuleNotFoundError) as exc:
        return FaceVerification(match=False, confidence=0.0, reason="La verificación biométrica no está disponible; solo se puede detectar rostros.", engine="opencv_haar", fallback_used=True)
    except ValueError as exc:
        return FaceVerification(match=False, confidence=0.0, reason=str(exc), engine="face_recognition", fallback_used=False)
    except Exception as exc:
        # Never claim identity verification after an engine failure. Detection is
        # still offered by the lightweight fallback for a useful, explicit result.
        logger.warning("Face verification engine failed; returning detection fallback: %s", exc)
        return FaceVerification(match=False, confidence=0.0, reason="No se pudo verificar la identidad; el servicio quedó en modo de detección.", engine="opencv_haar", fallback_used=True)


async def image_upload(file: UploadFile) -> bytes:
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Se requiere un archivo de imagen.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail="La imagen está vacía.")
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="La imagen excede el límite de 10 MB.")
    return content


app = FastAPI(title="Apuradito Face Service", version="1.0.0")


@app.middleware("http")
async def require_internal_token(request: Request, call_next):
    expected = os.getenv("AI_SERVICE_TOKEN", "").strip()
    if request.url.path != "/health" and expected:
        received = request.headers.get("X-Internal-Token", "")
        if not secrets.compare_digest(received, expected):
            return JSONResponse(status_code=401, content={"detail": "No autorizado."})
    return await call_next(request)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "face", "engine_preference": os.getenv("FACE_ENGINE", "face_recognition")}


@app.post("/v1/facial/detect", response_model=FaceDetection)
async def detect_face(file: UploadFile = File(...)) -> FaceDetection:
    try:
        return detect(await image_upload(file))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/facial/verify", response_model=FaceVerification)
async def verify_face(
    reference: UploadFile = File(...), probe: UploadFile = File(...), threshold: float = 0.60
) -> FaceVerification:
    if not 0.30 <= threshold <= 1.20:
        raise HTTPException(status_code=422, detail="threshold debe estar entre 0.30 y 1.20.")
    return verify(await image_upload(reference), await image_upload(probe), threshold)
