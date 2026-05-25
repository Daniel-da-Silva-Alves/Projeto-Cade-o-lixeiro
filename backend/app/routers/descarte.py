"""
Cadê o Lixeiro? v2.0 — Router: Locais de Descarte

Endpoints para consultar locais de descarte e gerenciar avaliações.
Ref: DSC-1 SDD §4.1
"""

import hashlib
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter(prefix="/api/descarte", tags=["descarte"])


class AvaliacaoCreate(BaseModel):
    estrelas: int = Field(..., ge=1, le=5)
    comentario: str | None = None


@router.get("")
async def listar_locais(
    bairro_id: UUID | None = None,
    tipo: str | None = None,
    busca: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Lista locais de descarte com filtros opcionais."""
    where_clauses = []
    params: dict = {}

    if bairro_id:
        where_clauses.append("ld.bairro_id = CAST(:bairro_id AS uuid)")
        params["bairro_id"] = str(bairro_id)
    if tipo:
        where_clauses.append(":tipo = ANY(ld.tipos_residuo)")
        params["tipo"] = tipo
    if busca:
        where_clauses.append(
            "(ld.nome ILIKE '%' || :busca || '%' OR ld.endereco ILIKE '%' || :busca || '%')"
        )
        params["busca"] = busca

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    query = text(f"""
        SELECT
            ld.id, ld.nome, ld.endereco,
            ld.latitude, ld.longitude,
            b.nome AS bairro,
            ld.tipos_residuo, ld.horarios, ld.telefone,
            COALESCE(AVG(ad.estrelas), 0) AS avaliacao_media,
            COUNT(ad.id) AS total_avaliacoes
        FROM public.locais_descarte ld
        JOIN public.bairros b ON b.id = ld.bairro_id
        LEFT JOIN public.avaliacoes_descarte ad ON ad.local_id = ld.id
        WHERE {where_sql}
        GROUP BY ld.id, ld.nome, ld.endereco, ld.latitude, ld.longitude,
                 b.nome, ld.tipos_residuo, ld.horarios, ld.telefone
        ORDER BY ld.nome
    """)

    result = await db.execute(query, params)

    locais = [
        {
            "id": str(row.id),
            "nome": row.nome,
            "endereco": row.endereco,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "bairro": row.bairro,
            "tipos_residuo": row.tipos_residuo or [],
            "horarios": row.horarios or {},
            "telefone": row.telefone,
            "avaliacao_media": round(float(row.avaliacao_media), 1),
            "total_avaliacoes": row.total_avaliacoes,
        }
        for row in result
    ]

    return {"locais": locais, "total": len(locais)}



@router.post("/{local_id}/avaliacao")
async def criar_avaliacao(
    local_id: UUID,
    avaliacao: AvaliacaoCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Cria avaliação anônima com rate limit por IP (1 por local por 24h)."""
    ip = request.client.host if request.client else "unknown"
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()

    # Rate limit: 1 avaliação por local por IP por 24h
    existente = await db.execute(text("""
        SELECT id FROM public.avaliacoes_descarte
        WHERE local_id = :local_id
          AND ip_hash = :ip_hash
          AND created_at > NOW() - INTERVAL '24 hours'
        LIMIT 1
    """), {"local_id": str(local_id), "ip_hash": ip_hash})

    if existente.first():
        raise HTTPException(
            status_code=429,
            detail="Você já avaliou este local nas últimas 24 horas.",
        )

    # Verificar se local existe
    local_exists = await db.execute(text(
        "SELECT id FROM public.locais_descarte WHERE id = :id"
    ), {"id": str(local_id)})
    if not local_exists.first():
        raise HTTPException(status_code=404, detail="Local não encontrado.")

    await db.execute(text("""
        INSERT INTO public.avaliacoes_descarte (local_id, estrelas, comentario, ip_hash)
        VALUES (:local_id, :estrelas, :comentario, :ip_hash)
    """), {
        "local_id": str(local_id),
        "estrelas": avaliacao.estrelas,
        "comentario": avaliacao.comentario,
        "ip_hash": ip_hash,
    })
    await db.commit()

    return {"sucesso": True, "mensagem": "Avaliação registrada!"}


@router.get("/{local_id}/avaliacoes")
async def listar_avaliacoes(
    local_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Lista avaliações de um local com paginação."""
    offset = (page - 1) * limit

    result = await db.execute(text("""
        SELECT estrelas, comentario, created_at
        FROM public.avaliacoes_descarte
        WHERE local_id = :local_id
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """), {"local_id": str(local_id), "limit": limit, "offset": offset})

    avaliacoes = [
        {
            "estrelas": row.estrelas,
            "comentario": row.comentario,
            "data": row.created_at.isoformat() if row.created_at else None,
        }
        for row in result
    ]

    # Total
    total_result = await db.execute(text(
        "SELECT COUNT(*) FROM public.avaliacoes_descarte WHERE local_id = :local_id"
    ), {"local_id": str(local_id)})
    total = total_result.scalar() or 0

    return {"avaliacoes": avaliacoes, "total": total, "page": page}
