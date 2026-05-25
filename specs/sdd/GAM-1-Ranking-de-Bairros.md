# 📐 SDD — GAM-1: Ranking de Bairros

> **Funcionalidade:** GAM-1 — Ranking de Sustentabilidade por Bairro
> **Documento:** Software Design Description
> **Norma de Referência:** IEEE 1016-2009
> **Versão:** 1.0
> **Data:** 24/05/2026
> **Requisito de Origem:** [GAM-1 — SRS](../srs/GAM-1-Ranking-de-Bairros.md)

---

## 1. Visão Geral e Stack

### 1.1 Contexto e Motivação

Gamificação por bairro baseada em denúncias resolvidas (peso 2) + descartes corretos (peso 1). O ranking é calculado via **Materialized View** atualizada a cada hora, garantindo performance sem recalcular a cada request.

---

## 2. Visão de Decomposição

### 2.1 Arquivos

```
frontend/
└── src/
    ├── lib/components/
    │   ├── TabelaRanking.svelte         ← Tabela com posição, bairro, pontuação
    │   ├── GraficoRanking.svelte        ← Gráfico de barras (Chart.js ou similar)
    │   └── WidgetTop3.svelte            ← Widget para home (medalhas)
    └── routes/ranking/+page.svelte

backend/
└── app/routers/ranking.py               ← GET /api/ranking
```

---

## 3. Modelagem de Dados

### 3.1 Materialized View: `mv_ranking_mensal`

```sql
CREATE MATERIALIZED VIEW mv_ranking_mensal AS
SELECT
    b.id AS bairro_id,
    b.nome AS bairro,
    COALESCE(den.total_resolvidas, 0) AS denuncias_resolvidas,
    COALESCE(aval.total_descartes, 0) AS descartes_corretos,
    (COALESCE(den.total_resolvidas, 0) * 2
     + COALESCE(aval.total_descartes, 0) * 1) AS pontuacao,
    EXTRACT(MONTH FROM now()) AS mes,
    EXTRACT(YEAR FROM now()) AS ano
FROM public.bairros b
LEFT JOIN (
    SELECT bairro_id, COUNT(*) AS total_resolvidas
    FROM public.denuncias
    WHERE status = 'resolvida'
      AND EXTRACT(MONTH FROM updated_at) = EXTRACT(MONTH FROM now())
      AND EXTRACT(YEAR FROM updated_at) = EXTRACT(YEAR FROM now())
    GROUP BY bairro_id
) den ON den.bairro_id = b.id
LEFT JOIN (
    SELECT ld.bairro_id, COUNT(*) AS total_descartes
    FROM public.avaliacoes_descarte ad
    JOIN public.locais_descarte ld ON ld.id = ad.local_id
    WHERE ad.estrelas >= 4
      AND EXTRACT(MONTH FROM ad.created_at) = EXTRACT(MONTH FROM now())
      AND EXTRACT(YEAR FROM ad.created_at) = EXTRACT(YEAR FROM now())
    GROUP BY ld.bairro_id
) aval ON aval.bairro_id = b.id
ORDER BY pontuacao DESC;

CREATE UNIQUE INDEX idx_mv_ranking_bairro ON mv_ranking_mensal (bairro_id);
```

### 3.2 Refresh Automático (pg_cron ou FastAPI scheduler)

```sql
-- Via Supabase pg_cron (se disponível no plano)
SELECT cron.schedule(
    'refresh-ranking',
    '0 * * * *',  -- A cada hora
    'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ranking_mensal'
);
```

Alternativa via FastAPI:

```python
# backend/app/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', hours=1)
async def refresh_ranking():
    async with get_db_session() as db:
        await db.execute(text(
            "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ranking_mensal"
        ))
        await db.commit()
```

---

## 4. Visão de Interface (Contratos)

### 4.1 Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/ranking?periodo=mensal` | Ranking mensal (MV) |
| GET | `/api/ranking?periodo=acumulado` | Ranking acumulado (query direta) |
| GET | `/api/ranking/top3` | Top 3 para widget da home |

### 4.2 Resposta

```json
{
  "ranking": [
    {
      "posicao": 1,
      "bairro": "Centro",
      "pontuacao": 42,
      "denuncias_resolvidas": 15,
      "descartes_corretos": 12,
      "variacao": 2  // subiu 2 posições vs mês anterior
    }
  ],
  "periodo": "mensal",
  "mes": 5,
  "ano": 2026
}
```

---

## 5. Mapeamento SRS → SDD

| Requisito SRS | Componente SDD | Status |
|---|---|---|
| **RF-GAM1-01** — Página `/ranking` | `routes/ranking/+page.svelte` | ✅ |
| **RF-GAM1-02** — Fórmula de pontuação | `(resolvidas × 2) + (descartes × 1)` na MV | ✅ |
| **RF-GAM1-03** — Filtro mensal/acumulado | Query param `?periodo=` | ✅ |
| **RF-GAM1-04** — Variação de posição | Comparação com snapshot do mês anterior | ✅ |
| **RF-GAM1-05** — Widget Top 3 | `WidgetTop3.svelte` + `GET /api/ranking/top3` | ✅ |
| **RF-GAM1-06** — Atualização a cada hora | `REFRESH MATERIALIZED VIEW CONCURRENTLY` | ✅ |
| **RF-GAM1-07** — Gráficos | `GraficoRanking.svelte` (Chart.js) | ✅ |

---

## 6. Decisões Arquiteturais

| # | Decisão | Justificativa |
|:-:|---------|---------------|
| 1 | Materialized View | Performance — ranking não muda a cada request. Refresh a cada hora é suficiente |
| 2 | `CONCURRENTLY` no refresh | Permite leitura durante atualização (sem lock) |
| 3 | Descartes = avaliações ≥ 4 estrelas | Proxy para "descarte correto" — cidadão avaliou positivamente o ponto |
| 4 | APScheduler como fallback para pg_cron | pg_cron pode não estar disponível no plano free do Supabase |
