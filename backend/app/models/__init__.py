"""
Cadê o Lixeiro? v2.0 — Models Package

Importa todos os models para facilitar acesso e garantir que
o SQLAlchemy os registre na metadata do Base.
"""

from app.models.bairro import Bairro
from app.models.caminhao import Caminhao
from app.models.motorista import Motorista
from app.models.rota import Rota, PontoRota
from app.models.local_descarte import LocalDescarte, AvaliacaoDescarte
from app.models.localizacao import LocalizacaoCaminhao, CacheGeocodificacao
from app.models.denuncia import Denuncia, TimelineStatus
from app.models.notificacao import SubscriptionPush, LogNotificacao

__all__ = [
    "Bairro",
    "Caminhao",
    "Motorista",
    "Rota",
    "PontoRota",
    "LocalDescarte",
    "AvaliacaoDescarte",
    "LocalizacaoCaminhao",
    "CacheGeocodificacao",
    "Denuncia",
    "TimelineStatus",
    "SubscriptionPush",
    "LogNotificacao",
]
