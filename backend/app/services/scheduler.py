"""
Cadê o Lixeiro? v2.0 — Scheduler: Tarefas Periódicas

1. Refresh da Materialized View ranking (a cada hora)
2. Limpeza de localizações antigas > 30 dias (a cada 6 horas)
3. Limpeza de logs de notificação > 7 dias (a cada 6 horas)
Ref: GAM-1 SDD §3.2
"""

import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_tasks: list = []


async def _refresh_mv_loop():
    """Refresh da MV ranking a cada hora."""
    while True:
        try:
            from app.database import async_session_factory
            from sqlalchemy import text

            async with async_session_factory() as db:
                await db.execute(text(
                    "REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_ranking_mensal"
                ))
                await db.commit()

            logger.info(
                f"[Scheduler] MV ranking refreshed at {datetime.now(timezone.utc).isoformat()}"
            )
        except Exception as e:
            logger.warning(f"[Scheduler] Erro ao refresh MV: {e}")

        await asyncio.sleep(3600)  # 1 hora


async def _cleanup_loop():
    """Limpeza de dados antigos a cada 6 horas."""
    # Esperar 30 min no startup para não sobrecarregar
    await asyncio.sleep(1800)

    while True:
        try:
            from app.database import async_session_factory
            from sqlalchemy import text

            async with async_session_factory() as db:
                # Limpar localizações > 30 dias
                result = await db.execute(text(
                    "SELECT public.limpar_localizacoes_antigas()"
                ))
                loc_removidas = result.scalar() or 0

                # Limpar logs de notificação > 7 dias
                result2 = await db.execute(text(
                    "SELECT public.limpar_logs_antigos()"
                ))
                logs_removidos = result2.scalar() or 0

                await db.commit()

            if loc_removidas or logs_removidos:
                logger.info(
                    f"[Scheduler] Cleanup: {loc_removidas} localizacoes, "
                    f"{logs_removidos} logs removidos"
                )
        except Exception as e:
            logger.warning(f"[Scheduler] Erro ao cleanup: {e}")

        await asyncio.sleep(21600)  # 6 horas


def iniciar_scheduler():
    """Inicia todas as tarefas periódicas em background."""
    global _tasks
    try:
        loop = asyncio.get_event_loop()

        _tasks.append(loop.create_task(_refresh_mv_loop()))
        _tasks.append(loop.create_task(_cleanup_loop()))

        logger.info("[Scheduler] Tarefas periodicas iniciadas (MV: 1h, Cleanup: 6h)")
    except Exception as e:
        logger.warning(f"[Scheduler] Nao foi possivel iniciar: {e}")
