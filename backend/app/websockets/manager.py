"""
Cadê o Lixeiro? v2.0 — WebSocket Connection Manager

Gerencia conexões de cidadãos (públicas) e motoristas (autenticadas).
Implementa broadcast de posições em tempo real.
Ref: RAT-1 SDD §4.1
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Gerencia conexões WebSocket de cidadãos e broadcast de posições."""

    def __init__(self):
        self.cidadaos: Set[WebSocket] = set()
        self.motoristas: Dict[str, WebSocket] = {}  # truck_id → ws
        self._estado_caminhoes: Dict[str, dict] = {}  # truck_id → último estado
        self._ultimo_update: Dict[str, float] = {}  # truck_id → timestamp (anti-spam)

    # --- Cidadãos ---

    async def conectar_cidadao(self, ws: WebSocket):
        """Aceita conexão de cidadão e envia estado inicial."""
        await ws.accept()
        self.cidadaos.add(ws)
        logger.info(f"[WS] Cidadão conectado. Total: {len(self.cidadaos)}")

        # Enviar estado atual de todos os caminhões online
        await ws.send_json({
            "tipo": "estado_inicial",
            "caminhoes": list(self._estado_caminhoes.values()),
        })

    def desconectar_cidadao(self, ws: WebSocket):
        """Remove cidadão desconectado."""
        self.cidadaos.discard(ws)
        logger.info(f"[WS] Cidadão desconectado. Total: {len(self.cidadaos)}")

    # --- Motoristas ---

    async def conectar_motorista(self, ws: WebSocket, truck_id: str):
        """Aceita conexão autenticada de motorista."""
        await ws.accept()
        self.motoristas[truck_id] = ws
        self._estado_caminhoes[truck_id] = {
            "truck_id": truck_id,
            "latitude": None,
            "longitude": None,
            "endereco": None,
            "status": "online",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(f"[WS] Motorista {truck_id} conectado. Total motoristas: {len(self.motoristas)}")

        # Notificar cidadãos
        await self.broadcast({
            "tipo": "caminhao_online",
            "truck_id": truck_id,
        })

    async def desconectar_motorista(self, truck_id: str):
        """Remove motorista e notifica cidadãos."""
        self.motoristas.pop(truck_id, None)
        # Atualizar estado para offline
        if truck_id in self._estado_caminhoes:
            self._estado_caminhoes[truck_id]["status"] = "offline"
        logger.info(f"[WS] Motorista {truck_id} desconectado.")

        await self.broadcast({
            "tipo": "caminhao_offline",
            "truck_id": truck_id,
        })

    # --- Broadcast ---

    async def broadcast(self, mensagem: dict):
        """Envia mensagem para TODOS os cidadãos conectados."""
        if not self.cidadaos:
            return

        mortos: Set[WebSocket] = set()
        for ws in self.cidadaos:
            try:
                await ws.send_json(mensagem)
            except Exception:
                mortos.add(ws)

        # Limpar conexões mortas
        if mortos:
            self.cidadaos -= mortos
            logger.info(f"[WS] Limpas {len(mortos)} conexões mortas. Restam: {len(self.cidadaos)}")

    async def receber_posicao(self, truck_id: str, lat: float, lng: float, endereco: str | None = None):
        """Recebe posição do motorista, atualiza estado e broadcast."""
        now = datetime.now(timezone.utc)

        # Anti-spam: ignorar updates < 3s
        ts_agora = now.timestamp()
        ultimo = self._ultimo_update.get(truck_id, 0)
        if (ts_agora - ultimo) < 3.0:
            return False  # Ignorado

        self._ultimo_update[truck_id] = ts_agora

        # Atualizar estado
        self._estado_caminhoes[truck_id] = {
            "truck_id": truck_id,
            "latitude": lat,
            "longitude": lng,
            "endereco": endereco,
            "status": "online",
            "timestamp": now.isoformat(),
        }

        # Broadcast
        await self.broadcast({
            "tipo": "posicao_atualizada",
            "truck_id": truck_id,
            "latitude": lat,
            "longitude": lng,
            "endereco": endereco,
            "timestamp": now.isoformat(),
        })

        return True

    # --- Estado ---

    def get_caminhoes_online(self) -> list[dict]:
        """Retorna lista de caminhões online."""
        return [
            c for c in self._estado_caminhoes.values()
            if c["status"] == "online"
        ]

    @property
    def total_cidadaos(self) -> int:
        return len(self.cidadaos)

    @property
    def total_motoristas(self) -> int:
        return len(self.motoristas)


# Instância global singleton
manager = ConnectionManager()
