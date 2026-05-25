# 📚 Cadê o Lixeiro? v2.0 — Índice de Especificações (SRS)

> **Projeto:** Cadê o Lixeiro? — Gestão Inteligente de Resíduos Urbanos
> **Stack:** SvelteKit (SPA) + Tailwind CSS v4 + FastAPI + Supabase (PostgreSQL/PostGIS + Auth + Storage) + Leaflet.js
> **Padrão:** IEEE 830 / ISO/IEC/IEEE 29148:2018

---

## Especificações de Requisitos de Software

| # | Código | Funcionalidade | Módulo | Complexidade | Arquivo |
|---|--------|---------------|--------|:------------:|---------|
| 1 | `INF-1` | [Página Sobre](./INF-1-Pagina-Sobre.md) | Informacional | ⭐ | `INF-1-Pagina-Sobre.md` |
| 2 | `AUT-2` | [Logout](./AUT-2-Logout.md) | Autenticação | ⭐ | `AUT-2-Logout.md` |
| 3 | `DSC-1` | [Locais de Descarte](./DSC-1-Locais-de-Descarte.md) | Descarte e Sustentabilidade | ⭐⭐ | `DSC-1-Locais-de-Descarte.md` |
| 4 | `HOR-1` | [Horários de Passagem](./HOR-1-Horarios-de-Passagem.md) | Rotas e Coleta | ⭐⭐ | `HOR-1-Horarios-de-Passagem.md` |
| 5 | `AUT-1` | [Login do Motorista](./AUT-1-Login-Motorista.md) | Autenticação | ⭐⭐ | `AUT-1-Login-Motorista.md` |
| 6 | `GAM-1` | [Ranking de Bairros](./GAM-1-Ranking-de-Bairros.md) | Gamificação | ⭐⭐ | `GAM-1-Ranking-de-Bairros.md` |
| 7 | `RAT-1` | [Rastreamento (Cidadão)](./RAT-1-Rastreamento-Cidadao.md) | Rastreamento | ⭐⭐⭐ | `RAT-1-Rastreamento-Cidadao.md` |
| 8 | `RAT-2` | [Compartilhamento de Localização](./RAT-2-Compartilhamento-Localizacao.md) | Rastreamento | ⭐⭐⭐ | `RAT-2-Compartilhamento-Localizacao.md` |
| 9 | `ROT-1` | [Rota de Coleta (Motorista)](./ROT-1-Rota-de-Coleta.md) | Rotas e Coleta | ⭐⭐⭐ | `ROT-1-Rota-de-Coleta.md` |
| 10 | `DEN-1` | [Denúncias Anônimas](./DEN-1-Denuncias.md) | Fiscalização | ⭐⭐⭐ | `DEN-1-Denuncias.md` |
| 11 | `NOT-1` | [Notificações Push](./NOT-1-Notificacoes-Push.md) | Comunicação | ⭐⭐⭐ | `NOT-1-Notificacoes-Push.md` |
| 12 | `ADM-1` | [Painel Administrativo](./ADM-1-Painel-Administrativo.md) | Administração | ⭐⭐⭐⭐ | `ADM-1-Painel-Administrativo.md` |

---

## Módulos do Sistema

| Módulo | Funcionalidades | Descrição |
|--------|:-:|-----------|
| **Informacional** | 1 | Página institucional sobre o projeto |
| **Autenticação** | 2 | Login CPF+Senha (JWT/Supabase Auth), Logout seguro |
| **Rastreamento** | 2 | Visualização em tempo real (cidadão) + Compartilhamento (motorista) via WebSocket |
| **Rotas e Coleta** | 2 | Horários de passagem + Visualização de rota do motorista |
| **Descarte e Sustentabilidade** | 1 | Locais de descarte com filtros, avaliações e horários |
| **Fiscalização** | 1 | Denúncias ambientais anônimas com fotos e acompanhamento |
| **Gamificação** | 1 | Ranking de sustentabilidade por bairro |
| **Comunicação** | 1 | Notificações push quando caminhão se aproxima |
| **Administração** | 1 | SQLAdmin (CRUD) + Dashboard Svelte (relatórios) |

---

## Próximos Passos

- [ ] Revisão e aprovação das SRS pelo stakeholder
- [ ] Criação das especificações técnicas (SDD) em `specs/sdd/`
- [ ] Setup do projeto SvelteKit + Tailwind CSS v4
- [ ] Setup do backend FastAPI + Supabase
- [ ] Início do desenvolvimento pela ordem de complexidade
