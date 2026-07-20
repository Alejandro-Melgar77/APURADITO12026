"""Fast, database-free contracts for the backend core."""

import unittest

from pydantic import ValidationError
from sqlalchemy.orm import configure_mappers

from app.core.config import Settings
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.models import Base
from app.schemas.ruta import BuscarRutaRequest, Coordenada, RutaPublicadaCreate
from app.schemas.viaje import SolicitudViajeCreate


class CoreContractsTest(unittest.TestCase):
    def test_plain_postgres_url_is_normalized_for_async_sqlalchemy(self) -> None:
        settings = Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            SECRET_KEY="a" * 32,
            DATABASE_URL="postgresql://user:password@host:5432/database",
        )
        self.assertEqual(
            settings.DATABASE_URL,
            "postgresql+asyncpg://user:password@host:5432/database",
        )

    def test_production_rejects_default_secret(self) -> None:
        with self.assertRaises(ValidationError):
            Settings(
                ENVIRONMENT="production",
                DEBUG=False,
                DATABASE_URL="postgresql://user:password@host:5432/database",
            )

    def test_access_and_refresh_tokens_are_not_interchangeable(self) -> None:
        access = create_access_token({"sub": "user-1"})
        refresh = create_refresh_token({"sub": "user-1"})
        self.assertEqual(verify_token(access)["type"], "access")
        self.assertEqual(verify_token(refresh, token_type="refresh")["type"], "refresh")
        with self.assertRaises(Exception):
            verify_token(refresh)

    def test_coordinates_and_search_limits_are_validated(self) -> None:
        with self.assertRaises(ValidationError):
            Coordenada(lon=181, lat=0)
        with self.assertRaises(ValidationError):
            BuscarRutaRequest(
                lon_pasajero=0,
                lat_pasajero=0,
                lon_destino=1,
                lat_destino=1,
                limite=51,
            )

    def test_route_and_trip_requests_reject_invalid_values(self) -> None:
        with self.assertRaises(ValidationError):
            RutaPublicadaCreate(
                origen_coor={"lon": 0, "lat": 0},
                destino_coor={"lon": 1, "lat": 1},
                linea_ruta_coor=[{"lon": 0, "lat": 0}],
                asientos_disponibles=1,
                hora_salida="2026-01-01T10:00:00",
            )
        with self.assertRaises(ValidationError):
            SolicitudViajeCreate(
                ruta_publicada_id="00000000-0000-0000-0000-000000000001",
                punto_abordaje={"lon": 0, "lat": 0},
                punto_desabordaje={"lon": 1, "lat": 1},
                distancia_caminata_abordaje_m=0,
                distancia_caminata_desabordaje_m=0,
                distancia_viaje_km=-1,
                costo_calculado_bs=0,
            )

    def test_canonical_models_have_a_valid_mapper_and_schema(self) -> None:
        configure_mappers()
        tables = set(Base.metadata.tables)
        self.assertIn("usuarios", tables)
        self.assertIn("rutas_publicadas", tables)
        self.assertIn("solicitudes_viaje", tables)
        self.assertIn("pagos", tables)


if __name__ == "__main__":
    unittest.main()
