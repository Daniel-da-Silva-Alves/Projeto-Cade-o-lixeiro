# 📐 SDD — NOT-1: Notificações Push

> **Funcionalidade:** NOT-1 — Notificações Push
> **Documento:** Software Design Description
> **Norma de Referência:** IEEE 1016-2009
> **Versão:** 1.0
> **Data:** 24/05/2026
> **Requisito de Origem:** [NOT-1 — SRS](../srs/NOT-1-Notificacoes-Push.md)

---

## 1. Visão Geral e Stack

### 1.1 Contexto e Motivação

Notifica cidadãos quando um caminhão entra no bairro que eles cadastraram. Usa Web Push API (VAPID) com Service Worker no frontend e disparo via FastAPI quando o rastreamento WebSocket detecta entrada no polígono do bairro (PostGIS `ST_Contains`).

---

## 2. Visão de Decomposição

### 2.1 Arquivos

```
frontend/
└── src/
    ├── lib/
    │   └── services/
    │       └── push.ts                  ← Registro de subscription
    ├── routes/horarios/+page.svelte     ← Botão "Ativar notificação"
    └── static/
        └── sw.js                        ← Service Worker para push

backend/
└── app/
    ├── routers/notificacoes.py          ← CRUD de subscriptions
    └── services/push.py                 ← Disparo via pywebpush
```

---

## 3. Modelagem de Dados

### 3.1 Tabela: `public.subscriptions_push`

```sql
CREATE TABLE public.subscriptions_push (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bairro_id   UUID NOT NULL REFERENCES public.bairros(id),
    endpoint    TEXT NOT NULL UNIQUE,
    p256dh      TEXT NOT NULL,
    auth_key    TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_subs_bairro ON public.subscriptions_push (bairro_id);
```

### 3.2 Tabela: `public.log_notificacoes` (anti-spam)

```sql
CREATE TABLE public.log_notificacoes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bairro_id   UUID NOT NULL,
    caminhao_id UUID NOT NULL,
    enviado_em  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_log_antispam ON public.log_notificacoes (bairro_id, caminhao_id, enviado_em);
```

---

## 4. Visão de Interface (Contratos)

### 4.1 Disparo de Notificação (Backend)

```python
# backend/app/services/push.py

async def verificar_e_notificar(db, caminhao_id: UUID, lat: float, lng: float):
    """Verifica se caminhão entrou em bairro com subscriptions ativas."""
    # 1. Identificar bairro pela posição
    bairro = await db.execute(
        select(Bairro).where(
            func.ST_Contains(Bairro.geom, func.ST_SetSRID(
                func.ST_MakePoint(lng, lat), 4326
            ))
        )
    )
    bairro = bairro.scalar_one_or_none()
    if not bairro:
        return

    # 2. Anti-spam: já notificou este bairro+caminhão na última hora?
    recente = await db.execute(
        select(LogNotificacao).where(
            LogNotificacao.bairro_id == bairro.id,
            LogNotificacao.caminhao_id == caminhao_id,
            LogNotificacao.enviado_em > datetime.utcnow() - timedelta(hours=1)
        )
    )
    if recente.scalar_one_or_none():
        return  # Já notificado

    # 3. Buscar subscriptions do bairro
    subs = await db.execute(
        select(SubscriptionPush).where(
            SubscriptionPush.bairro_id == bairro.id
        )
    )

    # 4. Enviar push para cada subscription
    for sub in subs.scalars():
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth_key}
                },
                data=json.dumps({
                    "title": "Cadê o Lixeiro?",
                    "body": f"O caminhão de coleta está chegando em {bairro.nome}!",
                    "icon": "/icon-192.png"
                }),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": "mailto:contato@cadeolixeiro.com"}
            )
        except WebPushException as e:
            if e.response and e.response.status_code == 410:
                await db.delete(sub)  # Subscription expirada

    # 5. Registrar log anti-spam
    db.add(LogNotificacao(bairro_id=bairro.id, caminhao_id=caminhao_id))
    await db.commit()
```

### 4.2 Integração com Rastreamento

A função `verificar_e_notificar` é chamada dentro do `driver_hub.py` (RAT-2) a cada posição recebida:

```python
# Em driver_hub.py, após broadcast da posição:
asyncio.create_task(
    verificar_e_notificar(db, caminhao_id, lat, lng)
)
```

---

## 5. Mapeamento SRS → SDD

| Requisito SRS | Componente SDD | Status |
|---|---|---|
| **RF-NOT1-01** — Botão "Ativar notificação" | Em `/horarios`, associado ao bairro | ✅ |
| **RF-NOT1-02** — Web Push API | `push.ts` + `sw.js` | ✅ |
| **RF-NOT1-03** — Registrar subscription | `POST /api/notificacoes/subscribe` | ✅ |
| **RF-NOT1-04** — Disparo por PostGIS | `ST_Contains` no `push.py` | ✅ |
| **RF-NOT1-05** — Conteúdo da notificação | JSON com title + body + icon | ✅ |
| **RF-NOT1-07** — Anti-spam 1h | `log_notificacoes` com check temporal | ✅ |

---

## 6. Decisões Arquiteturais

| # | Decisão | Justificativa |
|:-:|---------|---------------|
| 1 | `pywebpush` (Python) | Integra nativamente com FastAPI. Sem necessidade de serviço externo |
| 2 | Anti-spam via tabela `log_notificacoes` | Persistente entre reinícios do servidor |
| 3 | `asyncio.create_task` para notificação | Não bloqueia o fluxo de rastreamento |
| 4 | Limpeza de subscriptions 410 | Mantém tabela limpa automaticamente |
