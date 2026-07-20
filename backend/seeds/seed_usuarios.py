import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.usuario import Usuario
from app.models.conductor import Conductor
from app.models.vehiculo import Vehiculo
from app.models.ruta_publicada import RutaPublicada
from app.core.security import hash_password
import logging

logger = logging.getLogger(__name__)

async def seed_usuarios(db: AsyncSession):
    logger.info("Insertando usuarios y datos de prueba...")
    
    # 1. Crear Administrador
    res_admin = await db.execute(select(Usuario).where(Usuario.email == "admin@apuradito.bo"))
    admin = res_admin.scalar_one_or_none()
    
    if not admin:
        admin = Usuario(
            email="admin@apuradito.bo",
            password_hash=hash_password("Admin2026!"),
            nombre="Admin",
            apellido="Apuradito",
            ci_carnet="0000000",
            rol="admin",
            estado="activo",
            verificado_facial=True,
            saldo_coins=1000.00
        )
        db.add(admin)
        await db.flush()
    else:
        admin.password_hash = hash_password("Admin2026!")
        admin.nombre = admin.nombre or "Admin"
        admin.apellido = admin.apellido or "Apuradito"
        admin.ci_carnet = admin.ci_carnet or "0000000"
        admin.rol = "admin"
        admin.estado = "activo"
        admin.verificado_facial = True

    # 2. Crear Conductores de Prueba
    conductores_data = [
        {
            "email": "javier.doe@apuradito.bo",
            "password": "Conductor1!",
            "nombre": "Javier",
            "apellido": "Doe",
            "ci": "8765432",
            "placa": "1029-ABC",
            "marca": "Toyota",
            "modelo": "Corolla",
            "color": "Plateado",
            "anio": 2018,
            "tipo": "automovil",
            "combustible": "gasolina",
            "asientos": 4,
            # Ruta: UAGRM -> Plaza 24 de Septiembre (Centro)
            "orig_lon": -63.1915, "orig_lat": -17.7770, "orig_dir": "UAGRM (Av. Centenario)",
            "dest_lon": -63.1821, "dest_lat": -17.7833, "dest_dir": "Plaza 24 de Septiembre",
            "linea": "LINESTRING(-63.1915 -17.7770, -63.1870 -17.7800, -63.1821 -17.7833)"
        },
        {
            "email": "ana.lopez@apuradito.bo",
            "password": "Conductor2!",
            "nombre": "Ana",
            "apellido": "Lopez",
            "ci": "7654321",
            "placa": "1030-XYZ",
            "marca": "Suzuki",
            "modelo": "Gixxer",
            "color": "Negro",
            "anio": 2021,
            "tipo": "moto",
            "combustible": "gasolina",
            "asientos": 1,
            # Ruta: Equipetrol -> Plaza 24 de Septiembre
            "orig_lon": -63.1990, "orig_lat": -17.7690, "orig_dir": "Equipetrol (Av. San Martín)",
            "dest_lon": -63.1821, "dest_lat": -17.7833, "dest_dir": "Plaza 24 de Septiembre",
            "linea": "LINESTRING(-63.1990 -17.7690, -63.1910 -17.7750, -63.1821 -17.7833)"
        },
        {
            "email": "carlos.ruiz@apuradito.bo",
            "password": "Conductor3!",
            "nombre": "Carlos",
            "apellido": "Ruiz",
            "ci": "6543210",
            "placa": "1031-EFG",
            "marca": "Nissan",
            "modelo": "Sentra",
            "color": "Blanco",
            "anio": 2017,
            "tipo": "automovil",
            "combustible": "gas",
            "asientos": 4,
            # Ruta: Villa 1ro de Mayo -> UAGRM
            "orig_lon": -63.1360, "orig_lat": -17.7950, "orig_dir": "Villa 1ro de Mayo",
            "dest_lon": -63.1915, "dest_lat": -17.7770, "dest_dir": "UAGRM (Av. Centenario)",
            "linea": "LINESTRING(-63.1360 -17.7950, -63.1500 -17.7900, -63.1700 -17.7850, -63.1915 -17.7770)"
        }
    ]

    for cond in conductores_data:
        res_c = await db.execute(select(Usuario).where(Usuario.email == cond["email"]))
        if not res_c.scalar_one_or_none():
            u = Usuario(
                email=cond["email"],
                password_hash=hash_password(cond["password"]),
                nombre=cond["nombre"],
                apellido=cond["apellido"],
                ci_carnet=cond["ci"],
                rol="conductor",
                estado="activo",
                verificado_facial=True,
                saldo_coins=50.00
            )
            db.add(u)
            await db.flush()
            
            c = Conductor(
                usuario_id=u.id,
                calificacion_promedio=4.8
            )
            db.add(c)
            await db.flush()
            
            v = Vehiculo(
                conductor_id=c.id,
                placa=cond["placa"],
                marca=cond["marca"],
                modelo=cond["modelo"],
                color=cond["color"],
                anio=cond["anio"],
                tipo=cond["tipo"],
                combustible=cond["combustible"],
                asientos_totales=cond["asientos"],
                placa_verificada=True,
                activo=True
            )
            db.add(v)
            await db.flush()

            # Insertar una ruta predeterminada de prueba para cada conductor
            r = RutaPublicada(
                conductor_id=c.id,
                vehiculo_id=v.id,
                origen_punto=f"SRID=4326;POINT({cond['orig_lon']} {cond['orig_lat']})",
                origen_direccion=cond["orig_dir"],
                destino_punto=f"SRID=4326;POINT({cond['dest_lon']} {cond['dest_lat']})",
                destino_direccion=cond["dest_dir"],
                linea_ruta=f"SRID=4326;{cond['linea']}",
                distancia_total_km=5.2,
                duracion_estimada_min=15,
                asientos_disponibles=cond["asientos"],
                estado="programada",
                hora_salida=datetime.datetime.now() + datetime.timedelta(hours=2),
                es_simulacion=False
            )
            db.add(r)
            await db.flush()

    # 3. Crear Pasajeros de Prueba
    pasajeros_data = [
        {"email": "maria.garcia@apuradito.bo", "nombre": "Maria", "apellido": "Garcia", "ci": "9998887"},
        {"email": "luis.fernandez@apuradito.bo", "nombre": "Luis", "apellido": "Fernandez", "ci": "8887776"},
        {"email": "pedro.sanchez@apuradito.bo", "nombre": "Pedro", "apellido": "Sanchez", "ci": "7776665"}
    ]

    for pas in pasajeros_data:
        res_p = await db.execute(select(Usuario).where(Usuario.email == pas["email"]))
        if not res_p.scalar_one_or_none():
            u = Usuario(
                email=pas["email"],
                password_hash=hash_password("Pasajero1!"),
                nombre=pas["nombre"],
                apellido=pas["apellido"],
                ci_carnet=pas["ci"],
                rol="pasajero",
                estado="activo",
                verificado_facial=True,
                saldo_coins=100.00  # Con coins suficientes para probar cobros
            )
            db.add(u)
            
    await db.commit()
    logger.info("Usuarios y datos geoespaciales de prueba insertados exitosamente.")
