# 📐 SDD — ADM-1: Painel Administrativo

> **Funcionalidade:** ADM-1 — Painel Administrativo
> **Documento:** Software Design Description
> **Norma de Referência:** IEEE 1016-2009
> **Versão:** 1.0
> **Data:** 24/05/2026
> **Requisito de Origem:** [ADM-1 — SRS](../srs/ADM-1-Painel-Administrativo.md)

---

## 1. Visão Geral e Stack

### 1.1 Contexto e Motivação

O painel admin é dividido em duas camadas: **SQLAdmin** (CRUD automático a partir dos models SQLAlchemy) e **Dashboard Svelte** (relatórios e KPIs customizados). O SQLAdmin roda integrado ao FastAPI em `/admin/`, enquanto o dashboard roda no SvelteKit em `/admin`.

### 1.2 Stack Tecnológica

| Camada | Tecnologia | Uso |
|---|---|---|
| **CRUD** | SQLAdmin | Interface admin auto-gerada |
| **Dashboard** | SvelteKit + Chart.js | KPIs, gráficos, mapa em tempo real |
| **Auth Admin** | Supabase Auth (role `admin`) | Controle de acesso |

---

## 2. Visão de Decomposição

### 2.1 Arquivos

```
frontend/
└── src/routes/admin/
    ├── +layout.ts              ← Guard de auth admin
    ├── +page.svelte            ← Dashboard principal (KPIs)
    ├── denuncias/+page.svelte  ← Gestão de denúncias
    └── rastreamento/+page.svelte ← Mapa com todos os caminhões

backend/
└── app/
    ├── admin/
    │   └── setup.py            ← Configuração do SQLAdmin
    └── routers/
        └── admin.py            ← Endpoints de KPIs/relatórios
```

### 2.2 Configuração SQLAdmin

```python
# backend/app/admin/setup.py

from sqladmin import Admin, ModelView
from app.models import Caminhao, Motorista, Rota, PontoRota, 
    LocalDescarte, Bairro, Denuncia

class CaminhaoAdmin(ModelView, model=Caminhao):
    column_list = ["truck_id", "modelo", "placa", "status"]
    column_searchable_list = ["truck_id", "placa"]
    column_sortable_list = ["truck_id", "status"]

class MotoristaAdmin(ModelView, model=Motorista):
    column_list = ["nome", "cpf", "caminhao", "status"]
    column_searchable_list = ["nome", "cpf"]
    form_excluded_columns = ["auth_id", "created_at", "updated_at"]

    async def after_model_change(self, data, model, is_created, request):
        """Ao criar motorista, criar usuário no Supabase Auth."""
        if is_created:
            email = f"{model.cpf}@cadeolixeiro.internal"
            senha_temp = gerar_senha_temporaria()
            user = supabase.auth.admin.create_user({
                "email": email,
                "password": senha_temp,
                "email_confirm": True,
            })
            model.auth_id = user.user.id
            # Flash senha temporária para o admin
            request.session["senha_temp"] = senha_temp

class RotaAdmin(ModelView, model=Rota):
    column_list = ["rota_id", "caminhao", "bairro", "tipo_coleta", "dias_semana", "ativa"]

class DenunciaAdmin(ModelView, model=Denuncia):
    column_list = ["id_acompanhamento", "tipo", "status", "bairro", "created_at"]
    column_sortable_list = ["status", "created_at"]
    column_default_sort = [("status", False), ("created_at", True)]
    form_edit_rules = ["status"]  # Admin só pode editar status

    async def after_model_change(self, data, model, is_created, request):
        """Ao alterar status, registrar na timeline + impactar ranking."""
        if not is_created:
            timeline = TimelineStatus(
                denuncia_id=model.id,
                status_anterior=data.get("_old_status"),
                status_novo=model.status,
            )
            db.add(timeline)
            await db.commit()

def setup_admin(app, engine):
    admin = Admin(app, engine, title="Cadê o Lixeiro? — Admin")
    admin.add_view(CaminhaoAdmin)
    admin.add_view(MotoristaAdmin)
    admin.add_view(RotaAdmin)
    admin.add_view(DenunciaAdmin)
    admin.add_view(ModelView(LocalDescarte, name="Locais de Descarte"))
    admin.add_view(ModelView(Bairro, name="Bairros"))
```

---

## 3. Visão de Interface (Contratos)

### 3.1 Endpoints de KPIs (FastAPI)

```python
@router.get("/api/admin/kpis")
async def kpis(user = Depends(require_admin), db = Depends(get_db)):
    caminhoes_total = await db.execute(select(func.count()).select_from(Caminhao))
    caminhoes_online = await db.execute(
        select(func.count()).where(Caminhao.status == "online")
    )
    denuncias_pendentes = await db.execute(
        select(func.count()).where(Denuncia.status == "pendente")
    )
    rotas_total = await db.execute(
        select(func.count()).where(Rota.ativa == True)
    )
    locais_total = await db.execute(select(func.count()).select_from(LocalDescarte))

    return {
        "caminhoes": {"online": caminhoes_online.scalar(), "total": caminhoes_total.scalar()},
        "denuncias_pendentes": denuncias_pendentes.scalar(),
        "rotas_ativas": rotas_total.scalar(),
        "locais_descarte": locais_total.scalar(),
    }
```

### 3.2 Dashboard Svelte — Componentes

| Componente | Dados | Visualização |
|---|---|---|
| KPI Cards | `GET /api/admin/kpis` | Cards com números + ícones |
| Mapa de calor denúncias | `GET /api/admin/denuncias-heatmap` | Leaflet heatmap layer |
| Gráfico denúncias por status | `GET /api/admin/denuncias-por-status` | Chart.js (donut) |
| Ranking de bairros | `GET /api/ranking` | Chart.js (barras horizontais) |
| Mapa rastreamento admin | WebSocket `/ws/tracking` | Todos os caminhões em tempo real |

---

## 4. Mapeamento SRS → SDD

| Requisito SRS | Componente SDD | Status |
|---|---|---|
| **RF-ADM1-01** — CRUD Caminhões | SQLAdmin `CaminhaoAdmin` | ✅ |
| **RF-ADM1-02** — CRUD Motoristas | SQLAdmin `MotoristaAdmin` + Supabase Auth auto-create | ✅ |
| **RF-ADM1-03** — CRUD Rotas | SQLAdmin `RotaAdmin` | ✅ |
| **RF-ADM1-04** — CRUD Locais Descarte | SQLAdmin `ModelView(LocalDescarte)` | ✅ |
| **RF-ADM1-05** — CRUD Bairros | SQLAdmin `ModelView(Bairro)` | ✅ |
| **RF-ADM1-06** — Gestão Denúncias | SQLAdmin `DenunciaAdmin` (edita status, timeline auto) | ✅ |
| **RF-ADM1-07** — Auto-create Supabase Auth | `after_model_change` no MotoristaAdmin | ✅ |
| **RF-ADM1-08** — Auth admin | Guard com role check (`require_admin`) | ✅ |
| **RF-ADM1-09** — KPIs | `GET /api/admin/kpis` + cards Svelte | ✅ |
| **RF-ADM1-10** — Mapa de calor | Leaflet heatmap + dados de denúncias | ✅ |
| **RF-ADM1-13** — Rastreamento admin | WebSocket `/ws/tracking` no dashboard | ✅ |

---

## 5. Decisões Arquiteturais

| # | Decisão | Justificativa |
|:-:|---------|---------------|
| 1 | SQLAdmin para CRUD | Gerado automaticamente dos models SQLAlchemy. Zero código de interface |
| 2 | Dashboard separado em Svelte | UI customizada com gráficos e mapa que SQLAdmin não suporta |
| 3 | `after_model_change` para Supabase Auth | Hook do SQLAdmin — cria user automaticamente sem endpoint adicional |
| 4 | Role `admin` no JWT Supabase | Diferencia admin de motorista na mesma infraestrutura de auth |
