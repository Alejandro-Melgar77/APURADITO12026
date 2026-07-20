from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioResponse, UsuarioCreate, UsuarioUpdate
from app.core.security import hash_password

router = APIRouter()


@router.get("/", response_model=dict)
async def listar_usuarios(
    rol: Optional[str] = Query(
        None, description="Filtrar por rol: conductor, pasajero, ambos, admin"
    ),
    estado: Optional[str] = Query(
        None, description="Filtrar por estado: pendiente, activo, suspendido, eliminado"
    ),
    busqueda: Optional[str] = Query(
        None, description="Buscar por nombre, apellido, email o CI"
    ),
    pagina: int = Query(1, ge=1, description="Número de página"),
    por_pagina: int = Query(20, ge=1, le=100, description="Registros por página"),
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Usuario).where(Usuario.estado != "eliminado")

    if rol:
        query = query.where(Usuario.rol == rol)
    if estado:
        query = query.where(Usuario.estado == estado)
    if busqueda:
        busqueda_like = f"%{busqueda}%"
        query = query.where(
            or_(
                Usuario.nombre.ilike(busqueda_like),
                Usuario.apellido.ilike(busqueda_like),
                Usuario.email.ilike(busqueda_like),
                Usuario.ci_carnet.ilike(busqueda_like),
            )
        )

    # Conteo total para paginación
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Aplicar paginación
    offset = (pagina - 1) * por_pagina
    query = query.order_by(Usuario.creado_en.desc()).offset(offset).limit(por_pagina)

    result = await db.execute(query)
    usuarios = result.scalars().all()

    return {
        "datos": usuarios,
        "total": total,
        "pagina": pagina,
        "por_pagina": por_pagina,
    }


@router.get("/{id}", response_model=UsuarioResponse)
async def obtener_usuario(
    id: str,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Usuario).where(Usuario.id == id))
    user = result.scalar_one_or_none()
    if not user or user.estado == "eliminado":
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario_manual(
    req: UsuarioCreate,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Usuario).where(Usuario.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="El correo electrónico ya está registrado"
        )

    nuevo_usuario = Usuario(
        email=req.email,
        password_hash=hash_password(req.password),
        nombre=req.nombre,
        apellido=req.apellido,
        ci_carnet=req.ci_carnet,
        fecha_nacimiento=req.fecha_nacimiento,
        telefono=req.telefono,
        rol=req.rol,
        estado=req.estado,
    )
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.put("/{id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    id: str,
    req: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Usuario).where(Usuario.id == id))
    user = result.scalar_one_or_none()
    if not user or user.estado == "eliminado":
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{id}")
async def eliminar_usuario(
    id: str,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Usuario).where(Usuario.id == id))
    user = result.scalar_one_or_none()
    if not user or user.estado == "eliminado":
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.estado = "eliminado"
    await db.commit()
    return {"mensaje": "Usuario eliminado lógicamente de forma correcta"}


@router.patch("/{id}/estado")
async def cambiar_estado_usuario(
    id: str,
    estado: str,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if estado not in ["pendiente", "activo", "suspendido"]:
        raise HTTPException(status_code=400, detail="Estado de usuario no válido")

    result = await db.execute(select(Usuario).where(Usuario.id == id))
    user = result.scalar_one_or_none()
    if not user or user.estado == "eliminado":
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.estado = estado
    await db.commit()
    return {"mensaje": f"Estado del usuario cambiado a {estado} exitosamente"}
