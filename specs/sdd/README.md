# 📐 Cadê o Lixeiro? v2.0 — Índice de Design Técnico (SDD)

> **Projeto:** Cadê o Lixeiro? — Gestão Inteligente de Resíduos Urbanos
> **Padrão:** IEEE 1016-2009
> **Stack:** SvelteKit 5 (SPA) + Tailwind CSS v4 + FastAPI (Python 3.12) + Supabase (PostgreSQL/PostGIS)
> **Hosting:** Appwrite (frontend SPA) + Railway (FastAPI backend) + Supabase (banco/auth/storage)

---

## Decisões Transversais

| Decisão | Escolha |
|---------|---------|
| **Framework Frontend** | SvelteKit com adapter-static (SPA), Svelte 5 (runes) |
| **CSS** | Tailwind CSS v4 |
| **Backend** | FastAPI (Python 3.12) |
| **ORM** | SQLAlchemy 2.0 + GeoAlchemy2 |
| **Banco de Dados** | Supabase PostgreSQL + PostGIS |
| **Autenticação** | Supabase Auth (JWT) |
| **Storage** | Supabase Storage |
| **Migrações** | Supabase Migrations (CLI) |
| **Admin CRUD** | SQLAdmin |
| **Mapas** | Leaflet.js + Leaflet Routing Machine |
| **WebSocket** | FastAPI nativo |
| **Push** | Web Push API (VAPID) + pywebpush |
| **Hosting Frontend** | Appwrite (static) |
| **Hosting Backend** | Railway (Docker) |
| **Repositório** | Monorepo (`frontend/` + `backend/`) |
| **Testes** | Manuais (por enquanto) |
| **Idioma UI** | Português (pt-BR) |

---

## Estrutura de Rotas

| Rota | Acesso | Funcionalidade |
|------|--------|----------------|
| `/` | Público | Home + Rastreamento (RAT-1) |
| `/horarios` | Público | Horários de Passagem (HOR-1) |
| `/descarte` | Público | Locais de Descarte (DSC-1) |
| `/denunciar` | Público | Denúncias (DEN-1) |
| `/ranking` | Público | Ranking de Bairros (GAM-1) |
| `/sobre` | Público | Página Sobre (INF-1) |
| `/coletor` | Motorista | Área do Motorista (AUT-1, RAT-2, ROT-1) |
| `/admin` | Admin | Dashboard Admin (ADM-1) |

---

## Especificações de Design Técnico

| # | Código | Funcionalidade | Arquivo | Complexidade |
|---|--------|---------------|---------|:------------:|
| 1 | `INF-1` | [Página Sobre](./INF-1-Pagina-Sobre.md) | `INF-1-Pagina-Sobre.md` | ⭐ |
| 2 | `AUT-2` | [Logout](./AUT-2-Logout.md) | `AUT-2-Logout.md` | ⭐ |
| 3 | `AUT-1` | [Login do Motorista](./AUT-1-Login-Motorista.md) | `AUT-1-Login-Motorista.md` | ⭐⭐ |
| 4 | `DSC-1` | [Locais de Descarte](./DSC-1-Locais-de-Descarte.md) | `DSC-1-Locais-de-Descarte.md` | ⭐⭐ |
| 5 | `HOR-1` | [Horários de Passagem](./HOR-1-Horarios-de-Passagem.md) | `HOR-1-Horarios-de-Passagem.md` | ⭐⭐ |
| 6 | `ROT-1` | [Rota de Coleta](./ROT-1-Rota-de-Coleta.md) | `ROT-1-Rota-de-Coleta.md` | ⭐⭐ |
| 7 | `GAM-1` | [Ranking de Bairros](./GAM-1-Ranking-de-Bairros.md) | `GAM-1-Ranking-de-Bairros.md` | ⭐⭐ |
| 8 | `RAT-1` | [Rastreamento Cidadão](./RAT-1-Rastreamento-Cidadao.md) | `RAT-1-Rastreamento-Cidadao.md` | ⭐⭐⭐ |
| 9 | `RAT-2` | [Compartilhamento Localização](./RAT-2-Compartilhamento-Localizacao.md) | `RAT-2-Compartilhamento-Localizacao.md` | ⭐⭐⭐ |
| 10 | `DEN-1` | [Denúncias](./DEN-1-Denuncias.md) | `DEN-1-Denuncias.md` | ⭐⭐⭐ |
| 11 | `NOT-1` | [Notificações Push](./NOT-1-Notificacoes-Push.md) | `NOT-1-Notificacoes-Push.md` | ⭐⭐⭐ |
| 12 | `ADM-1` | [Painel Administrativo](./ADM-1-Painel-Administrativo.md) | `ADM-1-Painel-Administrativo.md` | ⭐⭐⭐⭐ |

---

## Diagrama ER Completo

```mermaid
erDiagram
    BAIRROS {
        uuid id PK
        text nome UK
        geometry geom
    }
    CAMINHOES {
        uuid id PK
        text truck_id UK
        text modelo
        text placa UK
        text status
    }
    MOTORISTAS {
        uuid id PK
        uuid auth_id FK
        text nome
        varchar cpf UK
        uuid caminhao_id FK
        text status
    }
    ROTAS {
        uuid id PK
        text rota_id UK
        uuid caminhao_id FK
        uuid bairro_id FK
        text tipo_coleta
        text_arr dias_semana
    }
    PONTOS_ROTA {
        uuid id PK
        uuid rota_id FK
        text endereco
        float latitude
        float longitude
        smallint ordem
        time horario_passagem
    }
    LOCALIZACOES_CAMINHAO {
        bigint id PK
        uuid caminhao_id FK
        float latitude
        float longitude
        text endereco
    }
    LOCAIS_DESCARTE {
        uuid id PK
        text nome
        uuid bairro_id FK
        text_arr tipos_residuo
        jsonb horarios
    }
    AVALIACOES_DESCARTE {
        uuid id PK
        uuid local_id FK
        smallint estrelas
        text comentario
    }
    DENUNCIAS {
        uuid id PK
        text id_acompanhamento UK
        text tipo
        text status
        uuid bairro_id FK
        text_arr fotos_urls
    }
    TIMELINE_STATUS {
        uuid id PK
        uuid denuncia_id FK
        text status_anterior
        text status_novo
    }
    SUBSCRIPTIONS_PUSH {
        uuid id PK
        uuid bairro_id FK
        text endpoint UK
    }
    CACHE_GEOCODIFICACAO {
        bigint id PK
        geometry geom
        text endereco
    }

    BAIRROS ||--o{ ROTAS : "bairro_id"
    BAIRROS ||--o{ LOCAIS_DESCARTE : "bairro_id"
    BAIRROS ||--o{ DENUNCIAS : "bairro_id"
    BAIRROS ||--o{ SUBSCRIPTIONS_PUSH : "bairro_id"
    CAMINHOES ||--o| MOTORISTAS : "caminhao_id"
    CAMINHOES ||--o{ ROTAS : "caminhao_id"
    CAMINHOES ||--o{ LOCALIZACOES_CAMINHAO : "caminhao_id"
    ROTAS ||--o{ PONTOS_ROTA : "rota_id"
    LOCAIS_DESCARTE ||--o{ AVALIACOES_DESCARTE : "local_id"
    DENUNCIAS ||--o{ TIMELINE_STATUS : "denuncia_id"
```

---

## Estrutura do Monorepo

```
Projeto-Cade-o-lixeiro/
├── specs/
│   ├── srs/                    ← Requisitos (12 arquivos)
│   └── sdd/                    ← Design técnico (12 arquivos)
├── frontend/                   ← SvelteKit + Tailwind CSS v4
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/     ← Componentes reutilizáveis
│   │   │   ├── stores/         ← Estado global (runes)
│   │   │   ├── services/       ← Chamadas à API
│   │   │   └── utils/          ← Utilitários (cpf, formatação)
│   │   └── routes/             ← Páginas (file-based routing)
│   ├── static/                 ← Assets estáticos + sw.js
│   └── svelte.config.js
├── backend/                    ← FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── models/             ← SQLAlchemy models
│   │   ├── routers/            ← Endpoints REST
│   │   ├── websockets/         ← WebSocket handlers
│   │   ├── services/           ← Lógica de negócio
│   │   ├── admin/              ← SQLAdmin config
│   │   └── main.py             ← App FastAPI
│   ├── Dockerfile
│   └── requirements.txt
├── supabase/
│   └── migrations/             ← SQL migrations
└── README.md
```

---

## Próximos Passos

- [ ] Revisão e aprovação das SDDs pelo stakeholder
- [ ] Setup do monorepo (frontend + backend)
- [ ] Migrations do banco (Supabase CLI)
- [ ] Desenvolvimento iterativo por funcionalidade
