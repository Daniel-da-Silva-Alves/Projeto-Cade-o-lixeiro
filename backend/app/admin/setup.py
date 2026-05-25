"""
Cadê o Lixeiro? v2.0 — SQLAdmin Configuration

CRUD admin auto-gerado a partir dos models SQLAlchemy.
Ref: ADM-1 SDD §2.2
"""

import logging

from sqladmin import Admin, ModelView

from app.models import (
    Caminhao, Motorista, Rota, PontoRota,
    LocalDescarte, Bairro, Denuncia, TimelineStatus,
    SubscriptionPush,
)

logger = logging.getLogger(__name__)


class CaminhaoAdmin(ModelView, model=Caminhao):
    name = "Caminhao"
    name_plural = "Caminhoes"
    icon = "fa-solid fa-truck"

    column_list = ["truck_id", "modelo", "placa", "status", "updated_at"]
    column_searchable_list = ["truck_id", "placa"]
    column_sortable_list = ["truck_id", "status", "updated_at"]
    column_default_sort = ("updated_at", True)
    form_excluded_columns = ["localizacoes", "motoristas", "rotas"]


class MotoristaAdmin(ModelView, model=Motorista):
    name = "Motorista"
    name_plural = "Motoristas"
    icon = "fa-solid fa-user"

    column_list = ["nome", "cpf", "status", "caminhao", "created_at"]
    column_searchable_list = ["nome", "cpf"]
    column_sortable_list = ["nome", "status", "created_at"]
    form_excluded_columns = ["created_at", "updated_at"]


class RotaAdmin(ModelView, model=Rota):
    name = "Rota"
    name_plural = "Rotas"
    icon = "fa-solid fa-route"

    column_list = ["rota_id", "caminhao", "bairro", "tipo_coleta", "dias_semana", "ativa"]
    column_searchable_list = ["rota_id"]
    column_sortable_list = ["rota_id", "tipo_coleta", "ativa"]
    form_excluded_columns = ["pontos", "created_at", "updated_at"]


class PontoRotaAdmin(ModelView, model=PontoRota):
    name = "Ponto de Rota"
    name_plural = "Pontos de Rota"
    icon = "fa-solid fa-map-pin"

    column_list = ["rota", "ordem", "endereco", "horario_passagem"]
    column_sortable_list = ["ordem"]
    form_excluded_columns = ["created_at"]


class LocalDescarteAdmin(ModelView, model=LocalDescarte):
    name = "Local de Descarte"
    name_plural = "Locais de Descarte"
    icon = "fa-solid fa-recycle"

    column_list = ["nome", "endereco", "bairro", "tipos_residuo"]
    column_searchable_list = ["nome", "endereco"]
    form_excluded_columns = ["avaliacoes", "created_at", "updated_at"]


class BairroAdmin(ModelView, model=Bairro):
    name = "Bairro"
    name_plural = "Bairros"
    icon = "fa-solid fa-map"

    column_list = ["nome"]
    column_searchable_list = ["nome"]
    form_excluded_columns = ["rotas", "locais_descarte", "denuncias", "subscriptions_push", "geom"]


class DenunciaAdmin(ModelView, model=Denuncia):
    name = "Denuncia"
    name_plural = "Denuncias"
    icon = "fa-solid fa-flag"

    column_list = ["id_acompanhamento", "tipo", "status", "bairro", "created_at"]
    column_searchable_list = ["id_acompanhamento"]
    column_sortable_list = ["status", "created_at"]
    column_default_sort = [("status", False), ("created_at", True)]
    form_excluded_columns = ["timeline", "ip_hash", "fotos_urls"]

    # Admin pode editar apenas status
    form_edit_rules = ["status"]


class SubscriptionPushAdmin(ModelView, model=SubscriptionPush):
    name = "Subscription Push"
    name_plural = "Subscriptions Push"
    icon = "fa-solid fa-bell"

    column_list = ["bairro", "endpoint", "created_at"]
    can_create = False  # Criado pelo frontend
    can_edit = False


def setup_admin(app, engine):
    """Configura o SQLAdmin no FastAPI app."""
    admin = Admin(
        app,
        engine,
        title="Cade o Lixeiro? - Admin",
        base_url="/admin/",
    )

    admin.add_view(CaminhaoAdmin)
    admin.add_view(MotoristaAdmin)
    admin.add_view(RotaAdmin)
    admin.add_view(PontoRotaAdmin)
    admin.add_view(LocalDescarteAdmin)
    admin.add_view(BairroAdmin)
    admin.add_view(DenunciaAdmin)
    admin.add_view(SubscriptionPushAdmin)

    logger.info("[Admin] SQLAdmin configurado em /admin/")
    return admin
