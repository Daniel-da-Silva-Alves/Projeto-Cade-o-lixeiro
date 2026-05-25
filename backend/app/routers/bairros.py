"""
Cadê o Lixeiro? v2.0 — Router: Bairros

Endpoint público para listar bairros de Manaus.
Pré-requisito de quase todas as funcionalidades.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.bairro import Bairro

router = APIRouter(prefix="/api/bairros", tags=["bairros"])


@router.get("")
async def listar_bairros(db: AsyncSession = Depends(get_db)):
    """Lista todos os bairros de Manaus ordenados por nome."""
    result = await db.execute(
        select(Bairro.id, Bairro.nome).order_by(Bairro.nome)
    )
    bairros = [
        {"id": str(row.id), "nome": row.nome}
        for row in result.all()
    ]
    return {"bairros": bairros, "total": len(bairros)}
