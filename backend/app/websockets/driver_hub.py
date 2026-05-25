"""
Cadê o Lixeiro? v2.0 — WebSocket: Driver Hub (Motorista)

Endpoint autenticado para motoristas transmitirem localização GPS.
Ref: RAT-2 SDD §4.1
"""

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.websockets.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


async def verificar_jwt_ws(token: str | None) -> dict | None:
    """Verifica JWT para WebSocket (via query param)."""
    if not token:
        return None

    try:
        import jwt
        from jwt import PyJWKClient
        from app.config import get_settings

        settings = get_settings()
        jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"

        try:
            jwks_client = PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256"],
                audience="authenticated",
                leeway=60,
            )
        except Exception:
            # Fallback HS256
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
                leeway=60,
            )

        return payload
    except Exception as e:
        logger.warning(f"[WS Driver] JWT inválido: {e}")
        return None


@router.websocket("/ws/driver/{truck_id}")
async def ws_motorista(websocket: WebSocket, truck_id: str):
    """
    WebSocket autenticado para motorista.
    - JWT via query param ?token=...
    - Recebe posições → persiste → broadcast para cidadãos.
    - Anti-spam: ignora updates < 3s (no manager).
    """
    # Validar JWT
    token = websocket.query_params.get("token")
    user = await verificar_jwt_ws(token)

    if not user:
        await websocket.close(code=4001, reason="Não autorizado")
        return

    # Conectar motorista
    await manager.conectar_motorista(websocket, truck_id)

    # Marcar caminhão como online no DB
    # Usamos uma sessão independente para não conflitar com o loop
    from app.database import async_session_factory
    async with async_session_factory() as db:
        await db.execute(text("""
            UPDATE public.caminhoes SET status = 'online', updated_at = NOW()
            WHERE truck_id = :truck_id
        """), {"truck_id": truck_id})
        await db.commit()

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("tipo") == "desconectar":
                logger.info(f"[WS Driver] {truck_id} solicitou desconexão.")
                break

            if data.get("tipo") == "posicao":
                lat = float(data.get("lat", 0))
                lng = float(data.get("lng", 0))

                # Broadcast (anti-spam é tratado no manager)
                aceito = await manager.receber_posicao(truck_id, lat, lng)

                if aceito:
                    # Persistir posição de forma assíncrona
                    asyncio.create_task(
                        _persistir_posicao(truck_id, lat, lng)
                    )

    except WebSocketDisconnect:
        logger.info(f"[WS Driver] {truck_id} desconectou.")
    except Exception as e:
        logger.error(f"[WS Driver] Erro {truck_id}: {e}")
    finally:
        # Desconectar e marcar offline
        await manager.desconectar_motorista(truck_id)

        async with async_session_factory() as db:
            await db.execute(text("""
                UPDATE public.caminhoes SET status = 'offline', updated_at = NOW()
                WHERE truck_id = :truck_id
            """), {"truck_id": truck_id})
            await db.commit()


async def _persistir_posicao(truck_id: str, lat: float, lng: float):
    """Persiste posição no DB de forma assíncrona + geocodifica."""
    try:
        from app.database import async_session_factory
        async with async_session_factory() as db:
            # Buscar caminhao_id
            result = await db.execute(text(
                "SELECT id FROM public.caminhoes WHERE truck_id = :tid"
            ), {"tid": truck_id})
            row = result.first()
            if not row:
                return

            caminhao_uuid = str(row.id)

            # Inserir localização
            await db.execute(text("""
                INSERT INTO public.localizacoes_caminhao (caminhao_id, latitude, longitude)
                VALUES (CAST(:cid AS uuid), :lat, :lng)
            """), {"cid": caminhao_uuid, "lat": lat, "lng": lng})

            # Atualizar posição atual
            await db.execute(text("""
                UPDATE public.caminhoes
                SET ultima_posicao_lat = :lat,
                    ultima_posicao_lng = :lng,
                    updated_at = NOW()
                WHERE truck_id = :tid
            """), {"lat": lat, "lng": lng, "tid": truck_id})

            await db.commit()

        # Geocodificação assíncrona (não bloqueia)
        from app.services.geocodificacao import geocodificar_e_atualizar
        asyncio.create_task(
            geocodificar_e_atualizar(truck_id, lat, lng)
        )

        # Notificações push (verifica se caminhão entrou em bairro com subs)
        from app.services.push import verificar_e_notificar
        asyncio.create_task(
            verificar_e_notificar(truck_id, lat, lng)
        )

    except Exception as e:
        logger.error(f"[DB] Erro ao persistir posição {truck_id}: {e}")

