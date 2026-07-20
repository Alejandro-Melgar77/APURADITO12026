"""
Script de seed masivo para Apuradito.
Genera datos de prueba de Marzo a Junio de 2026.
Uso: python scripts/seed_large.py  (desde el directorio backend/)
"""
import asyncio
import sys
import random
import uuid
from datetime import datetime, timedelta, date
from decimal import Decimal
from faker import Faker

sys.path.append('.')

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.usuario import Usuario
from app.models.conductor import Conductor
from app.models.vehiculo import Vehiculo
from app.models.ruta_publicada import RutaPublicada
from app.models.solicitud_viaje import SolicitudViaje
from app.models.pago import Pago
from app.models.recarga_coins import RecargaCoins
from app.models.calificacion import Calificacion
from app.models.reclamo import Reclamo

fake = Faker('es_ES')

# ── Lugares de Santa Cruz de la Sierra ──────────────────────────────────────
LUGARES_SCZ = [
    {"nombre": "UAGRM - Facultad de Tecnologia",       "lat": -17.776, "lng": -63.195},
    {"nombre": "Ventura Mall",                           "lat": -17.753, "lng": -63.198},
    {"nombre": "Plaza 24 de Septiembre",                 "lat": -17.783, "lng": -63.182},
    {"nombre": "Cine Center - 3er Anillo",               "lat": -17.794, "lng": -63.180},
    {"nombre": "Plan 3000 - Mercado Central",            "lat": -17.825, "lng": -63.132},
    {"nombre": "Villa 1ro de Mayo",                      "lat": -17.790, "lng": -63.120},
    {"nombre": "Equipetrol Norte",                       "lat": -17.760, "lng": -63.195},
    {"nombre": "Ucebol",                                 "lat": -17.745, "lng": -63.170},
    {"nombre": "Terminal Bimodal",                       "lat": -17.797, "lng": -63.174},
    {"nombre": "Hipermaxi - 4to Anillo",                 "lat": -17.768, "lng": -63.160},
    {"nombre": "Parque Urbano",                          "lat": -17.762, "lng": -63.197},
    {"nombre": "Hospital Municipal Modelo",              "lat": -17.781, "lng": -63.168},
]

def wkt_point(lat: float, lng: float) -> str:
    """Crea un WKT point para GeoAlchemy2."""
    return f"SRID=4326;POINT({lng} {lat})"

def rand_dt(start: date, end: date) -> datetime:
    """Fecha/hora aleatoria en el rango dado."""
    delta = (end - start).days
    d = start + timedelta(days=random.randrange(delta))
    return datetime(d.year, d.month, d.day, random.randint(5, 22), random.randint(0, 59))


async def run_seed():
    print("Iniciando seed masivo de datos (Marzo - Junio 2026)...")
    START = date(2026, 3, 1)
    END   = date(2026, 6, 30)

    async with AsyncSessionLocal() as db:
        try:
            # ── 1. PASAJEROS (50) ──────────────────────────────────────────
            print("  [1/6] Creando 50 pasajeros...")
            pasajeros: list[Usuario] = []
            for _ in range(50):
                u = Usuario(
                    email=fake.unique.email(),
                    password_hash=hash_password("password123"),
                    nombre=fake.first_name(),
                    apellido=fake.last_name(),
                    ci_carnet=str(fake.unique.random_number(digits=7, fix_len=True)),
                    fecha_nacimiento=fake.date_of_birth(minimum_age=18, maximum_age=60),
                    telefono=f"7{fake.numerify('#######')}",
                    rol="pasajero",
                    estado="activo",
                    saldo_coins=Decimal(str(random.randint(50, 800))),
                    creado_en=rand_dt(START, END),
                )
                db.add(u)
                pasajeros.append(u)

            await db.flush()

            # ── 2. CONDUCTORES (20) ─────────────────────────────────────────
            print("  [2/6] Creando 20 conductores + vehiculos...")
            vehiculos: list[Vehiculo] = []
            conductores_usuarios: list[Usuario] = []

            MARCAS  = ['Toyota', 'Nissan', 'Suzuki', 'Hyundai', 'Kia', 'Chevrolet']
            MODELOS = ['Corolla', 'Sentra', 'Swift', 'Accent', 'Rio', 'Aveo']
            COLORES = ['Blanco', 'Negro', 'Plata', 'Rojo', 'Azul', 'Gris']
            TIPOS   = ['Auto', 'Camioneta']
            LETRAS  = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'

            for i in range(20):
                uc = Usuario(
                    email=fake.unique.email(),
                    password_hash=hash_password("password123"),
                    nombre=fake.first_name(),
                    apellido=fake.last_name(),
                    ci_carnet=str(fake.unique.random_number(digits=7, fix_len=True)),
                    fecha_nacimiento=fake.date_of_birth(minimum_age=21, maximum_age=60),
                    telefono=f"6{fake.numerify('#######')}",
                    rol="conductor",
                    estado="activo",
                    verificado_facial=True,
                    saldo_coins=Decimal(str(random.randint(0, 200))),
                    creado_en=rand_dt(START, END),
                )
                db.add(uc)
                conductores_usuarios.append(uc)

            await db.flush()

            # Crear perfil Conductor y Vehiculo para cada usuario conductor
            cond_objs: list[Conductor] = []
            for uc in conductores_usuarios:
                c = Conductor(
                    usuario_id=uc.id,
                    calificacion_promedio=Decimal(str(round(random.uniform(3.5, 5.0), 2))),
                    total_viajes=random.randint(5, 120),
                    km_totales=Decimal(str(round(random.uniform(100, 5000), 2))),
                    comisiones_pendientes_bs=Decimal("0.00"),
                    cuenta_congelada=False,
                )
                db.add(c)
                cond_objs.append(c)

            await db.flush()

            for idx, c in enumerate(cond_objs):
                placa = (
                    f"{random.randint(1000,9999)}"
                    f"{''.join(random.choices(LETRAS, k=3))}"
                )
                marca = random.choice(MARCAS)
                v = Vehiculo(
                    conductor_id=c.id,
                    placa=placa,
                    marca=marca,
                    modelo=random.choice(MODELOS),
                    color=random.choice(COLORES),
                    anio=random.randint(2010, 2025),
                    tipo=random.choice(TIPOS),
                    combustible="Gasolina",
                    asientos_totales=random.choice([4, 5]),
                    placa_verificada=True,
                    activo=True,
                )
                db.add(v)
                vehiculos.append(v)

            await db.flush()

            # ── 3. RUTAS PUBLICADAS (150) ───────────────────────────────────
            print("  [3/6] Creando 150 rutas publicadas...")
            rutas: list[RutaPublicada] = []
            ESTADOS_RUTA = ["completada"] * 6 + ["activa"] * 3 + ["cancelada"] * 1

            for _ in range(150):
                v = random.choice(vehiculos)
                # Encontrar el conductor de ese vehículo
                cond = next(c for c in cond_objs if c.id == v.conductor_id)

                origen  = random.choice(LUGARES_SCZ)
                destino = random.choice([l for l in LUGARES_SCZ if l != origen])

                hora_sal = rand_dt(START, END)
                estado   = random.choice(ESTADOS_RUTA)
                costo    = Decimal(str(random.choice([5.00, 8.00, 10.00, 12.00, 15.00])))

                r = RutaPublicada(
                    conductor_id=cond.id,
                    vehiculo_id=v.id,
                    origen_punto=wkt_point(origen["lat"],  origen["lng"]),
                    origen_direccion=origen["nombre"],
                    destino_punto=wkt_point(destino["lat"], destino["lng"]),
                    destino_direccion=destino["nombre"],
                    distancia_total_km=Decimal(str(round(random.uniform(2, 25), 2))),
                    duracion_estimada_min=random.randint(10, 60),
                    asientos_disponibles=random.randint(1, 4),
                    estado=estado,
                    hora_salida=hora_sal,
                    hora_llegada_estimada=hora_sal + timedelta(minutes=random.randint(15, 60)),
                    creado_en=hora_sal - timedelta(hours=random.randint(1, 48)),
                )
                db.add(r)
                rutas.append(r)

            await db.flush()

            # ── 4. SOLICITUDES + PAGOS + CALIFICACIONES + RECLAMOS ──────────
            print("  [4/6] Creando solicitudes, pagos, calificaciones y reclamos...")
            solicitudes_completadas: list[tuple[SolicitudViaje, RutaPublicada]] = []

            METODOS_PAGO = ["coins", "coins", "coins", "efectivo"]
            TIPOS_RECLAMO = ["conduccion_peligrosa", "cobro_incorrecto", "comportamiento", "ruta_incorrecta"]
            ASUNTOS_RECLAMO = [
                "El conductor manejaba de forma peligrosa",
                "Me cobraron mas de lo acordado",
                "El conductor fue irrespetuoso",
                "La ruta tomada fue diferente a la publicada",
                "El vehiculo no correspondia al registrado",
            ]

            for ruta in rutas:
                num_sol = random.randint(0, min(3, ruta.asientos_disponibles + 1))
                candidatos = random.sample(pasajeros, num_sol)

                for pasajero in candidatos:
                    # Estado de la solicitud depende del estado de la ruta
                    if ruta.estado == "completada":
                        est_sol = "completado"
                    elif ruta.estado == "cancelada":
                        est_sol = random.choice(["cancelado", "rechazado"])
                    else:
                        est_sol = random.choice(["pendiente", "aceptado"])

                    # Punto de abordaje: origen de la ruta con pequeño offset
                    abordaje_lat = LUGARES_SCZ[0]["lat"] + random.uniform(-0.005, 0.005)
                    abordaje_lng = LUGARES_SCZ[0]["lng"] + random.uniform(-0.005, 0.005)
                    desabordaje_lat = LUGARES_SCZ[1]["lat"] + random.uniform(-0.005, 0.005)
                    desabordaje_lng = LUGARES_SCZ[1]["lng"] + random.uniform(-0.005, 0.005)

                    costo_viaje = Decimal(str(round(random.uniform(5, 20), 2)))
                    metodo = random.choice(METODOS_PAGO)

                    sol = SolicitudViaje(
                        pasajero_id=pasajero.id,
                        ruta_publicada_id=ruta.id,
                        punto_abordaje=wkt_point(abordaje_lat, abordaje_lng),
                        punto_desabordaje=wkt_point(desabordaje_lat, desabordaje_lng),
                        distancia_viaje_km=Decimal(str(round(random.uniform(1, 20), 2))),
                        costo_calculado_bs=costo_viaje,
                        estado=est_sol,
                        metodo_pago=metodo,
                        creado_en=ruta.creado_en + timedelta(minutes=random.randint(5, 120)),
                    )
                    db.add(sol)
                    await db.flush()

                    if est_sol == "completado":
                        solicitudes_completadas.append((sol, ruta, pasajero))

                        # Buscar usuario_id del conductor de esta ruta
                        cond_match = next((c for c in cond_objs if c.id == ruta.conductor_id), None)
                        conductor_usuario_id = cond_match.usuario_id if cond_match else ruta.conductor_id

                        # Pago
                        comision = round(float(costo_viaje) * 0.15, 2)
                        neto     = round(float(costo_viaje) - comision, 2)
                        pago = Pago(
                            solicitud_viaje_id=sol.id,
                            pagador_id=pasajero.id,
                            receptor_id=conductor_usuario_id,  # Corregido: usar usuario_id
                            monto_total_bs=costo_viaje,
                            monto_comision_app_bs=Decimal(str(comision)),
                            monto_neto_conductor_bs=Decimal(str(neto)),
                            estado="completado",
                            metodo=metodo,
                            creado_en=ruta.hora_salida + timedelta(minutes=random.randint(30, 90)),
                        )
                        db.add(pago)

                        # Calificacion (60% de los viajes completados)
                        if random.random() < 0.60:
                            calif = Calificacion(
                                solicitud_viaje_id=sol.id,
                                calificador_id=pasajero.id,
                                calificado_id=conductor_usuario_id,
                                estrellas=random.randint(3, 5),
                                comentario=fake.sentence() if random.random() > 0.4 else None,
                                creado_en=ruta.hora_salida + timedelta(hours=random.randint(1, 6)),
                            )
                            db.add(calif)

                        # Reclamo (4% de los viajes completados)
                        if random.random() < 0.04:
                            tipo_idx = random.randrange(len(TIPOS_RECLAMO))
                            reclamo = Reclamo(
                                usuario_id=pasajero.id,
                                solicitud_viaje_id=sol.id,
                                tipo=TIPOS_RECLAMO[tipo_idx],
                                asunto=ASUNTOS_RECLAMO[tipo_idx],
                                descripcion=fake.paragraph(nb_sentences=2),
                                estado=random.choice(["abierto", "en_revision", "resuelto"]),
                                creado_en=ruta.hora_salida + timedelta(hours=random.randint(2, 24)),
                            )
                            db.add(reclamo)

            await db.flush()

            # ── 5. RECARGAS DE COINS ────────────────────────────────────────
            print("  [5/6] Creando recargas de coins...")
            METODOS_RECARGA = ["qr", "transferencia", "efectivo"]
            for pasajero in pasajeros:
                # Cada pasajero hace entre 1 y 4 recargas en el periodo
                n_recargas = random.randint(1, 4)
                for _ in range(n_recargas):
                    monto = Decimal(str(random.choice([20.00, 50.00, 100.00, 200.00])))
                    recarga = RecargaCoins(
                        usuario_id=pasajero.id,
                        monto_bs=monto,
                        coins_acreditados=monto,  # 1:1
                        referencia_unica=str(uuid.uuid4())[:12].upper(),
                        estado="confirmado",
                        verificacion_automatica=random.random() > 0.3,
                        creado_en=rand_dt(START, END),
                    )
                    db.add(recarga)

            await db.flush()

            # ── 6. COMMIT FINAL ─────────────────────────────────────────────
            print("  [6/6] Guardando todo en la base de datos...")
            await db.commit()
            print("")
            print("="*60)
            print("OK - Seed masivo completado exitosamente!")
            print(f"   Pasajeros creados  : 50")
            print(f"   Conductores creados: 20")
            print(f"   Vehiculos creados  : 20")
            print(f"   Rutas creadas      : 150")
            print(f"   Solicitudes+Pagos  : variable (segun rutas)")
            print(f"   Recargas de coins  : ~140 (50 pasajeros x avg 2.8)")
            print("="*60)

        except Exception as e:
            await db.rollback()
            import traceback
            print("="*60)
            print("ERROR durante el seed:")
            traceback.print_exc()
            print("="*60)


if __name__ == "__main__":
    asyncio.run(run_seed())
