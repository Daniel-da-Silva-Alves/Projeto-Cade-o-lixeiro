"""
Cadê o Lixeiro? v2.0 — WebSocket: Tracking Hub (Cidadão)

Endpoint público para cidadãos receberem posições de caminhões em tempo real.
Ref: RAT-1 SDD §4.2
"""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websockets.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/tracking")
async def ws_tracking(websocket: WebSocket):
    """
    WebSocket público para cidadãos.
    - Ao conectar: recebe estado_inicial com todos os caminhões online.
    - Em loop: recebe broadcasts de posição (posicao_atualizada, caminhao_offline).
    - Sem autenticação necessária.
    """
    await manager.conectar_cidadao(websocket)

    try:
        while True:
            # Cidadão é read-only, mas precisa manter a conexão aberta
            # Recebemos pings/keep-alive do cliente
            data = await websocket.receive_text()
            # Aceita ping do cliente
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.warning(f"[WS Tracking] Erro: {e}")
    finally:
        manager.desconectar_cidadao(websocket)
