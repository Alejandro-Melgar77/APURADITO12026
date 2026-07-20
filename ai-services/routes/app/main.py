"""Batch-trained demand scoring and deterministic route recommendation service.

This service deliberately accepts historical trip records through HTTP instead of
connecting to the production database. The main backend can export only the
fields needed for training and keep database credentials private.
"""

import json
import math
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

import joblib
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sklearn.ensemble import RandomForestRegressor

EARTH_RADIUS_KM = 6371.0088
MIN_TRAINING_ROWS = 20
MODEL_VERSION = 1
MODEL_DIR = Path(os.getenv("ROUTE_MODEL_DIR", "./models"))
MODEL_PATH = MODEL_DIR / "route_demand.joblib"
MODEL_META_PATH = MODEL_DIR / "route_demand.json"
model_lock = Lock()


class Coordinate(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class HistoryTrip(BaseModel):
    completed_at: datetime
    origin: Coordinate
    destination: Coordinate
    passenger_count: int = Field(default=1, ge=1, le=20)
    completed: bool = True


class TrainingRequest(BaseModel):
    trips: list[HistoryTrip] = Field(min_length=1, max_length=100_000)


class TrainingResponse(BaseModel):
    trained: bool
    records_received: int
    records_used: int
    message: str
    model_updated_at: datetime | None = None


class CandidateRoute(BaseModel):
    route_id: str = Field(min_length=1, max_length=100)
    origin: Coordinate
    destination: Coordinate
    available_seats: int = Field(ge=0, le=100)
    price_bs: float = Field(ge=0, le=10_000)
    driver_rating: float = Field(default=5.0, ge=0, le=5)
    estimated_minutes: float | None = Field(default=None, ge=0, le=1_440)


class ScoreRequest(BaseModel):
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    passenger_origin: Coordinate
    passenger_destination: Coordinate
    candidates: list[CandidateRoute] = Field(min_length=1, max_length=200)
    limit: int = Field(default=5, ge=1, le=25)


class ScoredRoute(BaseModel):
    route_id: str
    score: float = Field(ge=0.0, le=1.0)
    predicted_demand: float = Field(ge=0.0)
    pickup_distance_km: float = Field(ge=0.0)
    destination_distance_km: float = Field(ge=0.0)
    reasons: list[str]


class ScoreResponse(BaseModel):
    routes: list[ScoredRoute]
    model_available: bool
    fallback_used: bool


def haversine_km(a: Coordinate, b: Coordinate) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a.lat, a.lng, b.lat, b.lng))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(h))


def cell(value: float) -> float:
    """A stable ~1 km grid feature; avoids memorising exact passenger coordinates."""
    return round(value, 2)


def features(at: datetime, origin: Coordinate, destination: Coordinate) -> list[float]:
    local = at.astimezone(timezone.utc)
    return [
        float(local.hour),
        float(local.weekday()),
        cell(origin.lat),
        cell(origin.lng),
        cell(destination.lat),
        cell(destination.lng),
        haversine_km(origin, destination),
    ]


def load_model() -> dict | None:
    if not MODEL_PATH.exists():
        return None
    try:
        saved = joblib.load(MODEL_PATH)
        if saved.get("version") != MODEL_VERSION:
            return None
        return saved
    except Exception:
        return None


def train(request: TrainingRequest) -> TrainingResponse:
    completed = [trip for trip in request.trips if trip.completed]
    if len(completed) < MIN_TRAINING_ROWS:
        return TrainingResponse(
            trained=False,
            records_received=len(request.trips),
            records_used=len(completed),
            message=f"Se requieren al menos {MIN_TRAINING_ROWS} viajes completados; se conservará el fallback heurístico.",
        )

    # Each row represents observed demand in a time/location context. A grouped
    # aggregation would be appropriate for a warehouse-scale training pipeline;
    # this bounded service favors a simple, reproducible batch model.
    x = np.asarray([features(t.completed_at, t.origin, t.destination) for t in completed])
    y = np.asarray([float(t.passenger_count) for t in completed])
    estimator = RandomForestRegressor(n_estimators=160, min_samples_leaf=2, random_state=42, n_jobs=1)
    estimator.fit(x, y)
    now = datetime.now(timezone.utc)
    payload = {"version": MODEL_VERSION, "estimator": estimator, "trained_at": now.isoformat(), "records": len(completed)}
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with model_lock:
        joblib.dump(payload, MODEL_PATH)
        MODEL_META_PATH.write_text(json.dumps({"version": MODEL_VERSION, "trained_at": now.isoformat(), "records": len(completed)}), encoding="utf-8")
    return TrainingResponse(trained=True, records_received=len(request.trips), records_used=len(completed), message="Modelo de demanda entrenado y persistido.", model_updated_at=now)


def predict_demand(saved: dict | None, request: ScoreRequest, route: CandidateRoute) -> tuple[float, bool]:
    if saved is None:
        # Transparent baseline: a short, available, highly-rated trip is likely
        # useful even before historical data accumulates.
        heuristic = max(0.0, 2.0 - haversine_km(route.origin, request.passenger_origin) / 2 + route.driver_rating / 5)
        return heuristic, True
    vector = np.asarray([features(request.requested_at, route.origin, route.destination)])
    return max(0.0, float(saved["estimator"].predict(vector)[0])), False


def score(request: ScoreRequest) -> ScoreResponse:
    saved = load_model()
    scored: list[ScoredRoute] = []
    demand_values: list[float] = []
    raw: list[tuple[CandidateRoute, float, bool, float, float]] = []
    for candidate in request.candidates:
        pickup = haversine_km(request.passenger_origin, candidate.origin)
        destination = haversine_km(request.passenger_destination, candidate.destination)
        demand, fallback = predict_demand(saved, request, candidate)
        demand_values.append(demand)
        raw.append((candidate, demand, fallback, pickup, destination))
    max_demand = max(demand_values) or 1.0
    max_price = max(route.price_bs for route, *_ in raw) or 1.0
    for candidate, demand, fallback, pickup, destination in raw:
        proximity = max(0.0, 1.0 - ((pickup + destination) / 10.0))
        seat_score = min(candidate.available_seats / 4.0, 1.0)
        rating = candidate.driver_rating / 5.0
        affordability = max(0.0, 1.0 - candidate.price_bs / max_price)
        demand_score = demand / max_demand
        final = 0.40 * proximity + 0.20 * seat_score + 0.15 * rating + 0.15 * affordability + 0.10 * demand_score
        reasons = [f"abordaje a {pickup:.2f} km", f"destino a {destination:.2f} km", f"{candidate.available_seats} asientos disponibles"]
        if saved:
            reasons.append("demanda estimada desde historial")
        else:
            reasons.append("score heurístico: aún no hay modelo entrenado")
        scored.append(ScoredRoute(route_id=candidate.route_id, score=round(final, 4), predicted_demand=round(demand, 3), pickup_distance_km=round(pickup, 3), destination_distance_km=round(destination, 3), reasons=reasons))
    scored.sort(key=lambda item: item.score, reverse=True)
    return ScoreResponse(routes=scored[:request.limit], model_available=saved is not None, fallback_used=saved is None)


app = FastAPI(title="Apuradito Route Intelligence Service", version="1.0.0")


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
    saved = load_model()
    return {"status": "ok", "service": "routes", "model_available": saved is not None, "model_records": saved.get("records", 0) if saved else 0}


@app.post("/v1/routes/train", response_model=TrainingResponse)
def train_routes(request: TrainingRequest) -> TrainingResponse:
    return train(request)


@app.post("/v1/routes/score", response_model=ScoreResponse)
def score_routes(request: ScoreRequest) -> ScoreResponse:
    return score(request)
