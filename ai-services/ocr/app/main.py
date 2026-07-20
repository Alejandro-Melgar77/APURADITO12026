import logging
import os
import re
import secrets
from functools import lru_cache

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

PLATE_PATTERN = re.compile(r"^\d{3,4}[A-Z]{3}$")


class PlateResponse(BaseModel):
    plate: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    raw_text: str = ""
    is_valid_format: bool = False
    engine: str
    fallback_used: bool


def normalize_plate(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def is_valid_bolivian_plate(value: str) -> bool:
    return bool(PLATE_PATTERN.fullmatch(normalize_plate(value)))


def decode_image(content: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("El archivo no contiene una imagen válida.")
    return image


def preprocess(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    return cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)


@lru_cache(maxsize=1)
def easyocr_reader():
    """Load the heavy model only when it is actually requested."""
    import easyocr  # Imported here so the Tesseract fallback can still run.

    return easyocr.Reader(["es", "en"], gpu=False, verbose=False)


def read_with_easyocr(image: np.ndarray) -> tuple[str, float, str]:
    results = easyocr_reader().readtext(
        image, allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )
    candidates = [(normalize_plate(text), float(confidence)) for _, text, confidence in results]
    raw_text = " ".join(text for text, _ in candidates)
    valid = [(text, confidence) for text, confidence in candidates if is_valid_bolivian_plate(text)]
    if valid:
        plate, confidence = max(valid, key=lambda item: item[1])
        return plate, confidence, raw_text
    if candidates:
        plate, confidence = max(candidates, key=lambda item: item[1])
        return plate, confidence, raw_text
    return "", 0.0, raw_text


def read_with_tesseract(image: np.ndarray) -> tuple[str, float, str]:
    import pytesseract

    text = pytesseract.image_to_string(
        image,
        config="--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    )
    plate = normalize_plate(text)
    # Tesseract's basic API does not provide a reliable confidence for a single
    # text line, so callers can distinguish its format-based confidence.
    confidence = 0.65 if is_valid_bolivian_plate(plate) else 0.20 if plate else 0.0
    return plate, confidence, text.strip()


def recognize(content: bytes) -> PlateResponse:
    image = preprocess(decode_image(content))
    requested_engine = os.getenv("OCR_ENGINE", "easyocr").lower()
    if requested_engine == "easyocr":
        try:
            plate, confidence, raw_text = read_with_easyocr(image)
            return PlateResponse(
                plate=plate,
                confidence=confidence,
                raw_text=raw_text,
                is_valid_format=is_valid_bolivian_plate(plate),
                engine="easyocr",
                fallback_used=False,
            )
        except Exception as exc:  # Model download/import problems must not hide a request.
            logger.warning("EasyOCR unavailable; using Tesseract fallback: %s", exc)

    plate, confidence, raw_text = read_with_tesseract(image)
    return PlateResponse(
        plate=plate,
        confidence=confidence,
        raw_text=raw_text,
        is_valid_format=is_valid_bolivian_plate(plate),
        engine="tesseract",
        fallback_used=True,
    )


app = FastAPI(title="Apuradito OCR Service", version="1.0.0")


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
    return {"status": "ok", "service": "ocr", "engine_preference": os.getenv("OCR_ENGINE", "easyocr")}


@app.post("/v1/ocr/plates", response_model=PlateResponse)
async def recognize_plate(file: UploadFile = File(...)) -> PlateResponse:
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Se requiere un archivo de imagen.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail="La imagen está vacía.")
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="La imagen excede el límite de 10 MB.")
    try:
        return recognize(content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
