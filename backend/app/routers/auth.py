"""
Cadê o Lixeiro? v2.0 — Router: Autenticação

Endpoint de validação de perfil do motorista autenticado.
Ref: AUT-1 SDD §4.3
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, CurrentUser
from app.models.motorista import Motorista

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/validar-perfil")
async def validar_perfil(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verifica se o motorista está ativo e com caminhão associado.
    Chamado pelo frontend após signInWithPassword do Supabase.
    """
    result = await db.execute(
        select(Motorista).where(Motorista.auth_id == user.id)
    )
    motorista = result.scalar_one_or_none()

    if not motorista:
        raise HTTPException(404, "Perfil de motorista não encontrado")

    return {
        "ativo": motorista.status == "ativo",
        "caminhao_id": str(motorista.caminhao_id) if motorista.caminhao_id else None,
        "nome": motorista.nome,
    }
