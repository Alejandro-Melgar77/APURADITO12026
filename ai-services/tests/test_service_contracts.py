import importlib.util
from pathlib import Path


ROOT = Path(__file__).parents[1]


def load_main(service: str):
    path = ROOT / service / "app" / "main.py"
    spec = importlib.util.spec_from_file_location(f"{service}_service_main", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def route_paths(module) -> set[str]:
    return {route.path for route in module.app.routes}


def test_ocr_contract_and_plate_normalization():
    ocr = load_main("ocr")
    assert {"/health", "/v1/ocr/plates"}.issubset(route_paths(ocr))
    assert ocr.normalize_plate("1234-abc") == "1234ABC"
    assert ocr.is_valid_bolivian_plate("1234-ABC") is True


def test_face_contract_without_loading_biometric_model():
    face = load_main("face")
    assert {"/health", "/v1/facial/detect", "/v1/facial/verify"}.issubset(route_paths(face))

