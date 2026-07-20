import logging
import math
import threading
import numpy as np
from sklearn.neighbors import BallTree
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class MatchingEngine:
    def __init__(self):
        self.tree = None
        self.routes_data = []
        self.is_fitted = False
        self.lock = threading.Lock()

    def update_model(self, routes_data: List[Dict[str, Any]]):
        """
        Update the model with available routes.
        routes_data: list of dicts with:
          id, lat_origen, lng_origen, calificacion, asientos_disponibles
        """
        with self.lock:
            self.routes_data = routes_data
            if not self.routes_data:
                self.tree = None
                self.is_fitted = False
                return

            coords = np.array([
                [math.radians(r["lat_origen"]), math.radians(r["lng_origen"])]
                for r in self.routes_data
            ])

            self.tree = BallTree(coords, metric='haversine')
            self.is_fitted = True

    def find_best_routes(
        self, 
        passenger_lat: float, 
        passenger_lng: float, 
        available_routes: List[Dict[str, Any]] = None, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Finds the best routes based on distance, rating, and available seats.
        """
        if available_routes is not None:
            self.update_model(available_routes)

        with self.lock:
            if not self.is_fitted or not self.routes_data:
                return []

            n = min(len(self.routes_data), max(top_k * 2, 10))
            
            q_coords = np.array([[math.radians(passenger_lat), math.radians(passenger_lng)]])
            distances, indices = self.tree.query(q_coords, k=n)

            R = 6371.0
            results = []

            for i, idx in enumerate(indices[0]):
                dist_km = distances[0][i] * R
                route = self.routes_data[idx]
                
                dist_score = max(0.0, 1.0 - (dist_km / 10.0))
                calificacion = float(route.get("calificacion", 5.0))
                rating_score = calificacion / 5.0
                
                asientos = int(route.get("asientos_disponibles", 1))
                seats_score = min(1.0, asientos / 4.0)

                final_score = (dist_score * 0.5) + (rating_score * 0.3) + (seats_score * 0.2)

                results.append({
                    "id": route["id"],
                    "score": float(final_score),
                    "distancia_km": float(dist_km),
                    "detalle": f"Dist: {dist_km:.2f}km, Cal: {calificacion}, Asientos: {asientos}"
                })

            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]

matching_engine = MatchingEngine()
