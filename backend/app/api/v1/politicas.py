from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_admin
from app.models.usuario import Usuario
from app.models.politica import Politica, ConsentimientoUsuario

router = APIRouter()


class PoliticaCreate(BaseModel):
    titulo: str
    contenido_html: str
    tipo: str  # 'terminos','privacidad','consentimiento_ubicacion','consentimiento_nfc','pagos'
    version: int = 1


class AceptarPoliticaRequest(BaseModel):
    aceptado: bool


@router.get("/")
async def listar_politicas_activas(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Politica).where(Politica.activa.is_(True)))
    return result.scalars().all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_politica(
    req: PoliticaCreate,
    current_user: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    # Desactivar la versión anterior del mismo tipo si existe
    result = await db.execute(
        select(Politica).where(and_(Politica.tipo == req.tipo, Politica.activa.is_(True)))
    )
    politica_anterior = result.scalar_one_or_none()
    if politica_anterior:
        politica_anterior.activa = False

    nueva_politica = Politica(
        titulo=req.titulo,
        contenido_html=req.contenido_html,
        tipo=req.tipo,
        version=req.version,
        activa=True,
    )
    db.add(nueva_politica)
    await db.commit()
    await db.refresh(nueva_politica)
    return nueva_politica


@router.get("/{id}")
async def obtener_politica(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Politica).where(Politica.id == id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Política no encontrada")
    return p


@router.post("/{id}/aceptar")
async def aceptar_politica(
    id: str,
    req: AceptarPoliticaRequest,
    request: Request,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Validar que exista la política
    result = await db.execute(select(Politica).where(Politica.id == id))
    politica = result.scalar_one_or_none()
    if not politica:
        raise HTTPException(status_code=404, detail="La política indicada no existe")

    # Verificar si ya existe el consentimiento para este usuario y política
    res_cons = await db.execute(
        select(ConsentimientoUsuario)
        .options(selectinload(ConsentimientoUsuario.politica))
        .where(
            and_(
                ConsentimientoUsuario.usuario_id == current_user.id,
                ConsentimientoUsuario.politica_id == politica.id,
            )
        )
    )
    consentimiento = res_cons.scalar_one_or_none()

    ip_addr = request.client.host if request.client else None

    if consentimiento:
        consentimiento.aceptado = req.aceptado
        consentimiento.ip_address = ip_addr
    else:
        consentimiento = ConsentimientoUsuario(
            usuario_id=current_user.id,
            politica_id=politica.id,
            aceptado=req.aceptado,
            ip_address=ip_addr,
        )
        db.add(consentimiento)

    await db.commit()
    return {
        "mensaje": "Consentimiento registrado correctamente",
        "aceptado": req.aceptado,
    }


@router.get("/usuario/consentimientos")
async def obtener_consentimientos_usuario(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ConsentimientoUsuario)
        .options(selectinload(ConsentimientoUsuario.politica))
        .where(
            ConsentimientoUsuario.usuario_id == current_user.id
        )
    )
    consentimientos = result.scalars().all()

    datos = []
    for c in consentimientos:
        datos.append(
            {
                "politica_id": str(c.politica_id),
                "titulo": c.politica.titulo,
                "tipo": c.politica.tipo,
                "version": c.politica.version,
                "aceptado": c.aceptado,
                "aceptado_en": c.aceptado_en.isoformat(),
            }
        )
    return datos
