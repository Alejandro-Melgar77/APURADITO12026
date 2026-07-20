import asyncio
import aiohttp
import math
from app.core.database import AsyncSessionLocal
from app.models.ruta_publicada import RutaPublicada

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # radio de la tierra en metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class SimulacionEngine:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SimulacionEngine, cls).__new__(cls, *args, **kwargs)
            cls._instance.posiciones_activas = {}
            cls._instance.task = None
        return cls._instance

    async def registrar_ruta(self, ruta_id, lat, lng, dest_lat, dest_lng, vel=40):
        url = f"http://router.project-osrm.org/route/v1/driving/{lng},{lat};{dest_lng},{dest_lat}?overview=full&geometries=geojson"
        
        waypoints = []
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("routes") and len(data["routes"]) > 0:
                            waypoints = data["routes"][0]["geometry"]["coordinates"] # [lng, lat]
        except Exception:
            pass
        
        if not waypoints:
            waypoints = [[lng, lat], [dest_lng, dest_lat]]

        self.posiciones_activas[str(ruta_id)] = {
            "lat": lat,
            "lng": lng,
            "vel_kmh": vel,
            "waypoints": waypoints,
            "waypoint_idx": 0,
            "progreso_seg": 0.0,
            "ruta_geojson": list(waypoints)
        }

        if self.task is None:
            self.task = asyncio.create_task(self._loop())
            
    def actualizar_velocidad(self, ruta_id: str, nueva_vel: float):
        if str(ruta_id) in self.posiciones_activas:
            self.posiciones_activas[str(ruta_id)]["vel_kmh"] = nueva_vel
            
    def actualizar_velocidad_global(self, nueva_vel: float):
        for ruta_id in self.posiciones_activas:
            self.posiciones_activas[ruta_id]["vel_kmh"] = nueva_vel

    async def _loop(self):
        while True:
            rutas_a_eliminar = []
            for ruta_id, pos in self.posiciones_activas.items():
                vel_kmh = pos["vel_kmh"]
                distancia_por_tick_m = (vel_kmh * 1000 / 3600) * 5
                
                distancia_restante = distancia_por_tick_m
                
                while distancia_restante > 0:
                    idx = pos["waypoint_idx"]
                    if idx >= len(pos["waypoints"]) - 1:
                        rutas_a_eliminar.append(ruta_id)
                        break
                        
                    w_curr = pos["waypoints"][idx]
                    w_next = pos["waypoints"][idx + 1]
                    
                    dist_total_seg = haversine(w_curr[1], w_curr[0], w_next[1], w_next[0])
                    dist_faltante_seg = dist_total_seg - pos["progreso_seg"]
                    
                    if distancia_restante >= dist_faltante_seg:
                        distancia_restante -= dist_faltante_seg
                        pos["waypoint_idx"] += 1
                        pos["progreso_seg"] = 0.0
                        pos["lat"] = w_next[1]
                        pos["lng"] = w_next[0]
                    else:
                        pos["progreso_seg"] += distancia_restante
                        frac = pos["progreso_seg"] / dist_total_seg if dist_total_seg > 0 else 0
                        pos["lat"] = w_curr[1] + (w_next[1] - w_curr[1]) * frac
                        pos["lng"] = w_curr[0] + (w_next[0] - w_curr[0]) * frac
                        distancia_restante = 0

            if rutas_a_eliminar:
                async with AsyncSessionLocal() as session:
                    for ruta_id in set(rutas_a_eliminar):
                        if ruta_id in self.posiciones_activas:
                            del self.posiciones_activas[ruta_id]
                        ruta = await session.get(RutaPublicada, ruta_id)
                        if ruta:
                            ruta.estado = "completada"
                    await session.commit()

            await asyncio.sleep(5)

    def detener(self):
        self.posiciones_activas.clear()
        if self.task:
            self.task.cancel()
            self.task = None

simulacion_engine = SimulacionEngine()
