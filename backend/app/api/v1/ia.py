from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List

from app.services.ai.facial_recognition import detect_faces
from app.services.ai.ocr_plates import read_license_plate
from app.services.ai.matching_engine import matching_engine

router = APIRouter()


@router.post("/facial-recognition")
async def api_facial_recognition(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        has_face = detect_faces(contents)
        return {"has_face": has_face}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr-plates")
async def api_ocr_plates(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        plate_text = read_license_plate(contents)
        return {"plate_text": plate_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class LocationUpdate(BaseModel):
    driver_id: str
    lat: float
    lon: float


@router.post("/matching/update-drivers")
def api_update_drivers(drivers: List[LocationUpdate]):
    drivers_data = [{"id": d.driver_id, "lat": d.lat, "lon": d.lon} for d in drivers]
    matching_engine.update_drivers(drivers_data)
    return {"status": "updated"}


class PassengerLocation(BaseModel):
    lat: float
    lon: float


@router.post("/matching/find-driver")
def api_find_driver(location: PassengerLocation):
    best_matches = matching_engine.find_best_match(location.lat, location.lon)
    return {"matched_driver_ids": best_matches}
