"""
Cadê o Lixeiro? v2.0 — Router: Ranking de Bairros

Endpoints para consultar o ranking de sustentabilidade por bairro.
Utiliza a Materialized View `mv_ranking_mensal`.
Ref: GAM-1 SDD §4.1
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter(prefix="/api/ranking", tags=["ranking"])


@router.get("")
async def listar_ranking(
    periodo: str = Query("mensal", pattern="^(mensal|acumulado)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista ranking de bairros.
    - `mensal`: Usa a Materialized View (atualizada a cada hora)
    - `acumulado`: Query direta para ranking all-time
    """
    if periodo == "mensal":
        result = await db.execute(text("""
            SELECT
                bairro_id, bairro,
                denuncias_resolvidas, descartes_corretos,
                pontuacao, mes, ano
            FROM mv_ranking_mensal
            ORDER BY pontuacao DESC, bairro ASC
        """))
    else:
        # Ranking acumulado (all-time) — query direta
        result = await db.execute(text("""
            SELECT
                b.id AS bairro_id,
                b.nome AS bairro,
                COALESCE(den.total_resolvidas, 0) AS denuncias_resolvidas,
                COALESCE(aval.total_descartes, 0) AS descartes_corretos,
                (COALESCE(den.total_resolvidas, 0) * 2
                 + COALESCE(aval.total_descartes, 0) * 1) AS pontuacao,
                0 AS mes,
                0 AS ano
            FROM public.bairros b
            LEFT JOIN (
                SELECT bairro_id, COUNT(*) AS total_resolvidas
                FROM public.denuncias
                WHERE status = 'resolvida'
                GROUP BY bairro_id
            ) den ON den.bairro_id = b.id
            LEFT JOIN (
                SELECT ld.bairro_id, COUNT(*) AS total_descartes
                FROM public.avaliacoes_descarte ad
                JOIN public.locais_descarte ld ON ld.id = ad.local_id
                WHERE ad.estrelas >= 4
                GROUP BY ld.bairro_id
            ) aval ON aval.bairro_id = b.id
            ORDER BY pontuacao DESC, b.nome ASC
        """))

    rows = result.mappings().all()
    ranking = [
        {
            "posicao": i + 1,
            "bairro_id": str(row["bairro_id"]),
            "bairro": row["bairro"],
            "denuncias_resolvidas": row["denuncias_resolvidas"],
            "descartes_corretos": row["descartes_corretos"],
            "pontuacao": row["pontuacao"],
        }
        for i, row in enumerate(rows)
    ]

    return {
        "ranking": ranking,
        "periodo": periodo,
        "total": len(ranking),
    }


@router.get("/top3")
async def top3(
    db: AsyncSession = Depends(get_db),
):
    """Top 3 bairros do ranking mensal para o widget da home."""
    result = await db.execute(text("""
        SELECT bairro_id, bairro, pontuacao,
               denuncias_resolvidas, descartes_corretos
        FROM mv_ranking_mensal
        ORDER BY pontuacao DESC, bairro ASC
        LIMIT 3
    """))

    rows = result.mappings().all()
    medalhas = ["🥇", "🥈", "🥉"]

    top = [
        {
            "posicao": i + 1,
            "medalha": medalhas[i],
            "bairro": row["bairro"],
            "pontuacao": row["pontuacao"],
            "denuncias_resolvidas": row["denuncias_resolvidas"],
            "descartes_corretos": row["descartes_corretos"],
        }
        for i, row in enumerate(rows)
    ]

    return {"top3": top}
