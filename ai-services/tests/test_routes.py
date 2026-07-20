import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

ROUTES_ROOT = Path(__file__).parents[1] / "routes"
sys.path.insert(0, str(ROUTES_ROOT))
import app.main as routes  # noqa: E402


def payload() -> dict:
    return {
        "passenger_origin": {"lat": -17.783, "lng": -63.182},
        "passenger_destination": {"lat": -17.80, "lng": -63.15},
        "candidates": [
            {"route_id": "close", "origin": {"lat": -17.784, "lng": -63.181}, "destination": {"lat": -17.801, "lng": -63.151}, "available_seats": 3, "price_bs": 7, "driver_rating": 4.8},
            {"route_id": "far", "origin": {"lat": -17.70, "lng": -63.10}, "destination": {"lat": -17.70, "lng": -63.10}, "available_seats": 1, "price_bs": 12, "driver_rating": 3.0},
        ],
    }


def test_score_has_heuristic_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(routes, "MODEL_DIR", tmp_path)
    monkeypatch.setattr(routes, "MODEL_PATH", tmp_path / "model.joblib")
    monkeypatch.setattr(routes, "MODEL_META_PATH", tmp_path / "model.json")
    response = TestClient(routes.app).post("/v1/routes/score", json=payload())
    assert response.status_code == 200
    assert response.json()["fallback_used"] is True
    assert response.json()["routes"][0]["route_id"] == "close"


def test_train_then_score_uses_model(tmp_path, monkeypatch):
    monkeypatch.setattr(routes, "MODEL_DIR", tmp_path)
    monkeypatch.setattr(routes, "MODEL_PATH", tmp_path / "model.joblib")
    monkeypatch.setattr(routes, "MODEL_META_PATH", tmp_path / "model.json")
    now = datetime.now(timezone.utc)
    trips = [
        {"completed_at": (now - timedelta(hours=index)).isoformat(), "origin": {"lat": -17.783, "lng": -63.182}, "destination": {"lat": -17.80, "lng": -63.15}, "passenger_count": 1 + index % 3}
        for index in range(20)
    ]
    client = TestClient(routes.app)
    train = client.post("/v1/routes/train", json={"trips": trips})
    assert train.status_code == 200 and train.json()["trained"] is True
    score = client.post("/v1/routes/score", json=payload())
    assert score.status_code == 200
    assert score.json()["model_available"] is True
    assert score.json()["fallback_used"] is False

