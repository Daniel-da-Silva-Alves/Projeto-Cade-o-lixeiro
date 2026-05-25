"""
Cadê o Lixeiro? v2.0 — Router: Rotas de Coleta

Endpoints para consulta de rotas por bairro e pontos de uma rota.
Ref: HOR-1 SDD §4.1
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, CurrentUser

router = APIRouter(prefix="/api/rotas", tags=["rotas"])



class BuscaPorBairro(BaseModel):
    bairro_ids: list[UUID]


@router.post("/por-bairro")
async def rotas_por_bairro(
    body: BuscaPorBairro,
    db: AsyncSession = Depends(get_db),
):
    """Busca rotas que passam pelos bairros selecionados."""
    if not body.bairro_ids:
        return {"rotas": []}

    ids_str = [str(bid) for bid in body.bairro_ids]
    placeholders = ", ".join(f":id_{i}" for i in range(len(ids_str)))

    query = text(f"""
        SELECT
            r.id, r.rota_id, r.tipo_coleta, r.dias_semana,
            r.endereco_inicio, r.endereco_fim, r.ativa,
            b.nome AS bairro,
            c.truck_id AS caminhao
        FROM public.rotas r
        JOIN public.bairros b ON b.id = r.bairro_id
        JOIN public.caminhoes c ON c.id = r.caminhao_id
        WHERE r.bairro_id IN ({placeholders})
          AND r.ativa = true
        ORDER BY b.nome, r.rota_id
    """)

    params = {f"id_{i}": uid for i, uid in enumerate(ids_str)}
    result = await db.execute(query, params)

    rotas = [
        {
            "id": str(row.id),
            "rota_id": row.rota_id,
            "bairro": row.bairro,
            "caminhao": row.caminhao,
            "tipo_coleta": row.tipo_coleta,
            "dias_semana": row.dias_semana or [],
            "endereco_inicio": row.endereco_inicio,
            "endereco_fim": row.endereco_fim,
        }
        for row in result
    ]

    return {"rotas": rotas, "total": len(rotas)}


@router.get("/{rota_id}/pontos")
async def pontos_da_rota(
    rota_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retorna pontos de uma rota com horários, ordenados."""
    # Verificar se rota existe
    rota_check = await db.execute(text(
        "SELECT id, rota_id FROM public.rotas WHERE id = :id"
    ), {"id": str(rota_id)})
    rota = rota_check.first()
    if not rota:
        raise HTTPException(status_code=404, detail="Rota não encontrada.")

    result = await db.execute(text("""
        SELECT
            id, endereco, latitude, longitude,
            cep, ordem, horario_passagem
        FROM public.pontos_rota
        WHERE rota_id = :rota_id
        ORDER BY ordem ASC
    """), {"rota_id": str(rota_id)})

    pontos = [
        {
            "id": str(row.id),
            "endereco": row.endereco,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "cep": row.cep,
            "ordem": row.ordem,
            "horario_passagem": str(row.horario_passagem) if row.horario_passagem else None,
        }
        for row in result
    ]

    return {
        "rota_id": rota.rota_id,
        "pontos": pontos,
        "total": len(pontos),
    }


@router.get("/minha-rota")
async def minha_rota(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna a rota atribuída ao motorista logado.
    Busca o caminhão via user.id → motoristas.user_id → caminhoes → rotas.
    """
    # 1. Buscar caminhão do motorista
    cam_result = await db.execute(text("""
        SELECT c.id, c.truck_id, c.placa, c.modelo
        FROM public.caminhoes c
        JOIN public.motoristas m ON m.caminhao_id = c.id
        WHERE m.user_id = CAST(:uid AS uuid)
        LIMIT 1
    """), {"uid": user.id})
    caminhao = cam_result.first()

    if not caminhao:
        raise HTTPException(status_code=404, detail="Nenhum caminhão associado ao motorista.")

    # 2. Buscar rota(s) ativas desse caminhão
    rotas_result = await db.execute(text("""
        SELECT
            r.id, r.rota_id, r.tipo_coleta, r.dias_semana,
            r.endereco_inicio, r.endereco_fim,
            b.nome AS bairro
        FROM public.rotas r
        JOIN public.bairros b ON b.id = r.bairro_id
        WHERE r.caminhao_id = CAST(:cid AS uuid)
          AND r.ativa = true
        ORDER BY r.rota_id
    """), {"cid": str(caminhao.id)})

    rotas = []
    for row in rotas_result:
        # Pontos de cada rota
        pontos_result = await db.execute(text("""
            SELECT id, endereco, latitude, longitude, ordem, horario_passagem
            FROM public.pontos_rota
            WHERE rota_id = CAST(:rid AS uuid)
            ORDER BY ordem ASC
        """), {"rid": str(row.id)})

        pontos = [
            {
                "id": str(p.id),
                "endereco": p.endereco,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "ordem": p.ordem,
                "horario_passagem": str(p.horario_passagem) if p.horario_passagem else None,
            }
            for p in pontos_result
        ]

        rotas.append({
            "id": str(row.id),
            "rota_id": row.rota_id,
            "bairro": row.bairro,
            "tipo_coleta": row.tipo_coleta,
            "dias_semana": row.dias_semana or [],
            "endereco_inicio": row.endereco_inicio,
            "endereco_fim": row.endereco_fim,
            "pontos": pontos,
        })

    return {
        "caminhao": {
            "id": str(caminhao.id),
            "truck_id": caminhao.truck_id,
            "placa": caminhao.placa,
            "modelo": caminhao.modelo,
        },
        "rotas": rotas,
    }
