# Cadê o Lixeiro?

**Gestão inteligente de resíduos urbanos para Manaus/AM** — rastreamento de caminhões de coleta em tempo real, horários de passagem, locais de descarte consciente, denúncias ambientais e ranking de bairros sustentáveis.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![SvelteKit](https://img.shields.io/badge/SvelteKit-Svelte%205-FF3E00?logo=svelte&logoColor=white)](https://svelte.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL%20+%20PostGIS-3FCF8E?logo=supabase&logoColor=white)](https://supabase.com)

---

## Overview

Cadê o Lixeiro? é uma plataforma cívica que conecta cidadãos ao serviço de coleta de lixo em Manaus. A aplicação permite acompanhar a posição dos caminhões de coleta via GPS em tempo real, consultar horários e rotas de passagem por bairro, encontrar ecopontos para descarte responsável, registrar denúncias ambientais geolocalizadas e receber notificações push quando o caminhão se aproxima.

> [!NOTE]
> Este é um projeto open source desenvolvido como portfólio técnico. Ele demonstra habilidades em arquitetura full-stack, comunicação em tempo real via WebSocket, geolocalização com PostGIS, e desenvolvimento de interfaces responsivas com Svelte 5.

## Features

- **Rastreamento em tempo real** — Mapa interativo com posições atualizadas via WebSocket e geocodificação reversa com cache PostGIS
- **Horários de passagem** — Consulta de rotas e pontos de coleta por bairro com visualização no mapa (polylines + marcadores)
- **Locais de descarte** — Ecopontos filtráveis por bairro e tipo de resíduo (orgânicos, recicláveis, eletrônicos, etc.) com avaliações
- **Denúncias ambientais** — Formulário com upload de fotos, marcador arrastável no mapa, detecção automática de bairro via PostGIS e acompanhamento por ID
- **Ranking de bairros** — Gamificação com ranking mensal/acumulado atualizado automaticamente via Materialized View
- **Notificações push** — Alerta quando um caminhão entra no bairro do cidadão, com anti-spam (1 push/bairro/caminhão/hora)
- **Painel admin** — Dashboard com KPIs, gráficos de denúncias e CRUD completo via SQLAdmin
- **PWA** — Instalável como aplicativo, com Service Worker para push notifications

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | SvelteKit (Svelte 5 + Runes) · Tailwind CSS v4 · Leaflet.js · TypeScript |
| **Backend** | FastAPI · SQLAlchemy 2.0 (async) · GeoAlchemy2 · uvloop · WebSocket nativo |
| **Database** | Supabase (PostgreSQL + PostGIS) · Row Level Security · Materialized Views |
| **Auth** | Supabase Auth (JWT ES256/HS256) |
| **Storage** | Supabase Storage (fotos de denúncias) |
| **Notifications** | Web Push (pywebpush + VAPID) |
| **Admin** | SQLAdmin (8 ModelViews) |
| **Deploy** | Docker (backend) · Static adapter (frontend SPA) |

## Architecture

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│    SvelteKit     │◄──────────────────►│     FastAPI      │
│   (Svelte 5)    │     REST API       │   (async/await)  │
│                 │◄──────────────────►│                  │
│  Leaflet.js     │                    │  SQLAlchemy 2.0  │
│  Tailwind v4    │                    │  GeoAlchemy2     │
└────────┬────────┘                    └────────┬─────────┘
         │                                      │
         │  Supabase Auth (JWT)                 │  asyncpg
         ▼                                      ▼
┌───────────────────────────────────────────────────────────┐
│                    Supabase                               │
│  PostgreSQL + PostGIS  │  Auth  │  Storage  │  RLS       │
└───────────────────────────────────────────────────────────┘
```

## Project Structure

```
├── frontend/              SvelteKit SPA
│   └── src/
│       ├── lib/
│       │   ├── components/    UI components (Mapa, Ranking, Upload, etc.)
│       │   ├── stores/        Svelte 5 rune stores (tracking, auth)
│       │   ├── services/      Push notifications, API clients
│       │   └── utils/         CPF validation, formatters
│       └── routes/            Pages (/, /horarios, /descarte, /denunciar, etc.)
├── backend/               FastAPI API
│   └── app/
│       ├── models/            13 SQLAlchemy models (GeoAlchemy2)
│       ├── routers/           8 route modules (REST endpoints)
│       ├── services/          Geocoding, push, scheduler
│       ├── websockets/        tracking_hub + driver_hub
│       └── admin/             SQLAdmin setup (8 ModelViews)
├── supabase/              Migrations + seed data
│   ├── migrations/            4 SQL migrations (tables, views, RLS)
│   └── seed/                  63 bairros + sample data
└── specs/                 Documentation
    ├── srs/                   Software Requirements Specifications
    ├── sdd/                   Software Design Documents
    └── ROADMAP.md             Implementation roadmap (7 phases)
```

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) 20+
- [Python](https://python.org/) 3.12+
- A [Supabase](https://supabase.com) project with **PostGIS** enabled

### Frontend

```bash
cd frontend
cp .env.example .env          # Configure Supabase URL, anon key, API URL
npm install
npm run dev                   # → http://localhost:5173
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # Configure DATABASE_URL, Supabase keys, JWT secret
uvicorn app.main:app --reload # → http://localhost:8000
```

> [!TIP]
> The backend includes interactive API docs at `/docs` (Swagger) and `/redoc`.

### Database

Apply the migrations in order via the Supabase SQL Editor or CLI:

```bash
# Migrations (in order)
supabase/migrations/001_tabelas_base.sql
supabase/migrations/002_funcionalidades.sql
supabase/migrations/003_views_indices.sql
supabase/migrations/004_rls.sql

# Seed data (63 neighborhoods of Manaus + sample routes/locations)
supabase/seed/001_bairros.sql
```

### Environment Variables

<details>
<summary>Backend (<code>.env</code>)</summary>

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (asyncpg) |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Service role key (server-side only) |
| `SUPABASE_ANON_KEY` | Anonymous key |
| `JWT_SECRET` | Supabase JWT secret |
| `VAPID_PRIVATE_KEY` | VAPID private key for push notifications |
| `VAPID_PUBLIC_KEY` | VAPID public key |
| `VAPID_CLAIMS_EMAIL` | Contact email for VAPID |

</details>

<details>
<summary>Frontend (<code>.env</code>)</summary>

| Variable | Description |
|----------|-------------|
| `PUBLIC_SUPABASE_URL` | Supabase project URL |
| `PUBLIC_SUPABASE_ANON_KEY` | Anonymous key |
| `PUBLIC_API_URL` | Backend API base URL |
| `PUBLIC_WS_URL` | WebSocket base URL |

</details>

## User Profiles

| Profile | Auth | Capabilities |
|---------|:----:|-------------|
| Citizen | — | Live map, schedules, disposal locations, complaints, neighborhood ranking |
| Driver | CPF login | Share GPS location, view assigned route, start/stop collection |
| Admin | Login | Dashboard with KPIs, manage all entities via SQLAdmin |

## Documentation

The `specs/` directory contains comprehensive documentation following industry standards:

- [Implementation Roadmap](./specs/ROADMAP.md) — 7-phase development checklist with dependency graph
- [Software Requirements (SRS)](./specs/srs/) — Functional requirements per feature
- [Software Design (SDD)](./specs/sdd/) — Technical architecture, data models, API contracts

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/bairros` | List all 63 neighborhoods |
| `GET` | `/api/ranking` | Neighborhood sustainability ranking |
| `GET` | `/api/descarte` | Disposal locations (filterable) |
| `POST` | `/api/denuncias` | Submit environmental complaint |
| `POST` | `/api/rotas/por-bairro` | Routes by neighborhood |
| `GET` | `/api/auth/validar-perfil` | Validate driver profile |
| `WS` | `/ws/tracking` | Real-time truck positions (public) |
| `WS` | `/ws/driver/{truck_id}` | Driver GPS sharing (authenticated) |

## Author

**Daniel da Silva Alves**

This project was designed, architected and built as a full-stack portfolio piece showcasing real-world skills in systems design, real-time communication, geospatial data, and modern web development.
