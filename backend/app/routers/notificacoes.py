"""
Cadê o Lixeiro? v2.0 — Router: Notificações Push

Endpoints para registrar/cancelar subscriptions de Web Push.
Ref: NOT-1 SDD §4.1
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter(prefix="/api/notificacoes", tags=["notificacoes"])


class SubscribeRequest(BaseModel):
    bairro_id: UUID
    endpoint: str
    p256dh: str
    auth_key: str


@router.post("/subscribe")
async def subscribe(
    body: SubscribeRequest,
    db: AsyncSession = Depends(get_db),
):
    """Registra uma subscription de Web Push para um bairro."""
    # Verificar se bairro existe
    bairro_check = await db.execute(text(
        "SELECT id FROM public.bairros WHERE id = CAST(:bid AS uuid)"
    ), {"bid": str(body.bairro_id)})
    if not bairro_check.first():
        raise HTTPException(status_code=404, detail="Bairro nao encontrado.")

    # Upsert: se endpoint já existe, atualizar
    result = await db.execute(text("""
        INSERT INTO public.subscriptions_push (bairro_id, endpoint, p256dh, auth_key)
        VALUES (CAST(:bid AS uuid), :endpoint, :p256dh, :auth_key)
        ON CONFLICT (endpoint)
        DO UPDATE SET bairro_id = CAST(:bid AS uuid), p256dh = :p256dh, auth_key = :auth_key
        RETURNING id
    """), {
        "bid": str(body.bairro_id),
        "endpoint": body.endpoint,
        "p256dh": body.p256dh,
        "auth_key": body.auth_key,
    })
    row = result.first()
    await db.commit()

    return {
        "id": str(row.id),
        "bairro_id": str(body.bairro_id),
        "status": "subscribed",
    }


@router.delete("/subscribe/{sub_id}")
async def unsubscribe(
    sub_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Remove uma subscription de Web Push."""
    result = await db.execute(text("""
        DELETE FROM public.subscriptions_push
        WHERE id = CAST(:sid AS uuid)
        RETURNING id
    """), {"sid": str(sub_id)})

    if not result.first():
        raise HTTPException(status_code=404, detail="Subscription nao encontrada.")

    await db.commit()
    return {"status": "unsubscribed"}


@router.get("/status")
async def push_status(
    bairro_id: UUID | None = None,
    endpoint: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Verifica se existe subscription ativa para o endpoint/bairro."""
    if not endpoint:
        return {"subscribed": False}

    params: dict = {"endpoint": endpoint}
    query = "SELECT id, bairro_id FROM public.subscriptions_push WHERE endpoint = :endpoint"

    if bairro_id:
        query += " AND bairro_id = CAST(:bid AS uuid)"
        params["bid"] = str(bairro_id)

    result = await db.execute(text(query), params)
    row = result.first()

    if row:
        return {"subscribed": True, "id": str(row.id), "bairro_id": str(row.bairro_id)}
    return {"subscribed": False}
