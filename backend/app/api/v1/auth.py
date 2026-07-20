from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.models.usuario import Usuario
from app.models.conductor import Conductor
from app.models.vehiculo import Vehiculo
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RegistroPasajeroRequest,
    RegistroConductorRequest,
)
from app.schemas.usuario import UsuarioResponse
from app.api.deps import get_current_active_user

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Buscar usuario por email
    result = await db.execute(select(Usuario).where(Usuario.email == login_data.email))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Correo electrónico o contraseña incorrectos",
        )

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Correo electrónico o contraseña incorrectos",
        )

    if user.estado == "suspendido":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta cuenta ha sido suspendida. Comuníquese con administración.",
        )

    if user.estado == "eliminado":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    if user.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Tu cuenta aun esta pendiente de verificacion. "
                "Completa la validacion de identidad y vehiculo para activarla."
            ),
        )

    # Generar tokens
    user_id_str = str(user.id)
    access_token = create_access_token(data={"sub": user_id_str, "rol": user.rol})
    refresh_token = create_refresh_token(data={"sub": user_id_str})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "usuario": user,
    }


@router.post(
    "/registro/pasajero",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_pasajero(
    req: RegistroPasajeroRequest, db: AsyncSession = Depends(get_db)
):
    # Verificar si el email existe
    result = await db.execute(select(Usuario).where(Usuario.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado",
        )

    if req.ci_carnet:
        result_ci = await db.execute(
            select(Usuario).where(Usuario.ci_carnet == req.ci_carnet)
        )
        if result_ci.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="El carnet ya esta registrado")

    # Crear usuario pasajero
    nuevo_usuario = Usuario(
        email=req.email,
        password_hash=hash_password(req.password),
        nombre=req.nombre,
        apellido=req.apellido,
        ci_carnet=req.ci_carnet,
        fecha_nacimiento=req.fecha_nacimiento,
        telefono=req.telefono,
        rol="pasajero",
        estado="activo",  # Los pasajeros inician activos por defecto en el MVP
    )

    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post(
    "/registro/conductor",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_conductor(
    req: RegistroConductorRequest, db: AsyncSession = Depends(get_db)
):
    # Verificar si el email existe
    result = await db.execute(select(Usuario).where(Usuario.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado",
        )

    result_ci = await db.execute(
        select(Usuario).where(Usuario.ci_carnet == req.ci_carnet)
    )
    if result_ci.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El carnet ya esta registrado")

    # Verificar placa única
    res_placa = await db.execute(
        select(Vehiculo).where(Vehiculo.placa == req.placa.upper())
    )
    if res_placa.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La placa del vehículo ya está registrada en el sistema",
        )

    # 1. Crear usuario conductor (comienza en estado 'pendiente' hasta verificación facial y de placa)
    nuevo_usuario = Usuario(
        email=req.email,
        password_hash=hash_password(req.password),
        nombre=req.nombre,
        apellido=req.apellido,
        ci_carnet=req.ci_carnet,
        fecha_nacimiento=req.fecha_nacimiento,
        telefono=req.telefono,
        rol="conductor",
        estado="pendiente",
    )
    db.add(nuevo_usuario)
    await db.flush()  # Para obtener el ID

    # 2. Crear registro de Conductor
    nuevo_conductor = Conductor(usuario_id=nuevo_usuario.id)
    db.add(nuevo_conductor)
    await db.flush()

    # 3. Registrar su vehículo inicial
    nuevo_vehiculo = Vehiculo(
        conductor_id=nuevo_conductor.id,
        placa=req.placa.upper(),
        marca=req.marca,
        modelo=req.modelo,
        color=req.color,
        anio=req.anio,
        tipo=req.tipo,
        combustible=req.combustible,
        asientos_totales=req.asientos_totales,
        activo=True,
    )
    db.add(nuevo_vehiculo)

    await db.commit()
    await db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/refresh")
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    # Verificar el token
    payload = verify_token(refresh_token, token_type="refresh")
    user_id = payload.get("sub")

    result = await db.execute(select(Usuario).where(Usuario.id == user_id))
    user = result.scalar_one_or_none()

    if not user or user.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo o no encontrado",
        )

    access_token = create_access_token(data={"sub": str(user.id), "rol": user.rol})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UsuarioResponse)
async def obtener_mi_perfil(current_user: Usuario = Depends(get_current_active_user)):
    return current_user
