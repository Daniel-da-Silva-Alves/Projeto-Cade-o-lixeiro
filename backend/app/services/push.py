"""
Cadê o Lixeiro? v2.0 — Serviço de Notificações Push

Disparo de Web Push via pywebpush quando caminhão entra em bairro.
Anti-spam: max 1 push por bairro+caminhão por hora.
Ref: NOT-1 SDD §4.1
"""

import json
import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings

logger = logging.getLogger(__name__)


async def verificar_e_notificar(
    caminhao_truck_id: str,
    lat: float,
    lng: float,
):
    """
    Verifica se caminhão entrou em bairro com subscriptions ativas.
    Executada como asyncio.create_task (não bloqueia o WS loop).
    """
    try:
        from app.database import async_session_factory
        settings = get_settings()

        # Sem VAPID configurado, não faz nada
        if not settings.VAPID_PRIVATE_KEY:
            return

        async with async_session_factory() as db:
            # 1. Identificar bairro pela posição
            bairro_result = await db.execute(text("""
                SELECT id, nome
                FROM public.bairros
                WHERE geom IS NOT NULL
                  AND ST_Contains(
                    geom,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)
                  )
                LIMIT 1
            """), {"lat": lat, "lng": lng})

            bairro = bairro_result.first()
            if not bairro:
                return

            # 2. Buscar UUID do caminhão
            cam_result = await db.execute(text(
                "SELECT id FROM public.caminhoes WHERE truck_id = :tid"
            ), {"tid": caminhao_truck_id})
            cam = cam_result.first()
            if not cam:
                return

            caminhao_uuid = str(cam.id)
            bairro_uuid = str(bairro.id)

            # 3. Anti-spam: já notificou este bairro+caminhão na última hora?
            uma_hora_atras = datetime.now(timezone.utc) - timedelta(hours=1)
            antispam_result = await db.execute(text("""
                SELECT id FROM public.log_notificacoes
                WHERE bairro_id = CAST(:bid AS uuid)
                  AND caminhao_id = CAST(:cid AS uuid)
                  AND enviado_em > :corte
                LIMIT 1
            """), {"bid": bairro_uuid, "cid": caminhao_uuid, "corte": uma_hora_atras})

            if antispam_result.first():
                return  # Já notificado na última hora

            # 4. Buscar subscriptions do bairro
            subs_result = await db.execute(text("""
                SELECT id, endpoint, p256dh, auth_key
                FROM public.subscriptions_push
                WHERE bairro_id = CAST(:bid AS uuid)
            """), {"bid": bairro_uuid})

            subs = subs_result.fetchall()
            if not subs:
                return

            # 5. Enviar push para cada subscription
            try:
                from pywebpush import webpush, WebPushException
            except ImportError:
                logger.warning("[Push] pywebpush não instalado. Notificações desativadas.")
                return

            payload = json.dumps({
                "title": "Cade o Lixeiro?",
                "body": f"O caminhao de coleta esta chegando em {bairro.nome}!",
                "icon": "/icon-192.png",
                "tag": f"coleta-{bairro.nome}",
            })

            mortos = []
            enviados = 0

            for sub in subs:
                try:
                    webpush(
                        subscription_info={
                            "endpoint": sub.endpoint,
                            "keys": {"p256dh": sub.p256dh, "auth": sub.auth_key},
                        },
                        data=payload,
                        vapid_private_key=settings.VAPID_PRIVATE_KEY,
                        vapid_claims={"sub": settings.VAPID_CLAIMS_EMAIL},
                    )
                    enviados += 1
                except WebPushException as e:
                    if e.response and e.response.status_code == 410:
                        mortos.append(str(sub.id))
                    else:
                        logger.warning(f"[Push] Erro envio: {e}")
                except Exception as e:
                    logger.warning(f"[Push] Erro inesperado: {e}")

            # 6. Limpar subscriptions expiradas (410 Gone)
            for sub_id in mortos:
                await db.execute(text(
                    "DELETE FROM public.subscriptions_push WHERE id = CAST(:sid AS uuid)"
                ), {"sid": sub_id})

            # 7. Registrar log anti-spam
            if enviados > 0:
                await db.execute(text("""
                    INSERT INTO public.log_notificacoes (bairro_id, caminhao_id)
                    VALUES (CAST(:bid AS uuid), CAST(:cid AS uuid))
                """), {"bid": bairro_uuid, "cid": caminhao_uuid})

            await db.commit()
            if enviados:
                logger.info(f"[Push] {enviados} notificacoes enviadas para {bairro.nome}")

    except Exception as e:
        logger.error(f"[Push] Erro em verificar_e_notificar: {e}")
