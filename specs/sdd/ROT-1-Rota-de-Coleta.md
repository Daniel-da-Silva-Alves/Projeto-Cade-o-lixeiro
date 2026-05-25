# 📐 SDD — ROT-1: Rota de Coleta (Motorista)

> **Funcionalidade:** ROT-1 — Visualização de Rota de Coleta
> **Documento:** Software Design Description
> **Norma de Referência:** IEEE 1016-2009
> **Versão:** 1.0
> **Data:** 24/05/2026
> **Requisito de Origem:** [ROT-1 — SRS](../srs/ROT-1-Rota-de-Coleta.md)

---

## 1. Visão Geral e Stack

### 1.1 Contexto e Motivação

O motorista autenticado visualiza sua rota de coleta no mapa com todos os pontos de parada, endereços e horários. A rota é carregada automaticamente com base no caminhão associado ao motorista logado.

---

## 2. Visão de Decomposição

### 2.1 Arquivos

```
frontend/
└── src/
    ├── lib/components/
    │   ├── TabelaPontosRota.svelte     ← Tabela colapsável com pontos
    │   └── MapaRotaMotorista.svelte    ← Mapa com rota + ícones diferenciados
    └── routes/coletor/+page.svelte     ← Página do motorista

backend/
└── app/routers/rotas.py                ← GET /api/rotas/minha-rota (autenticado)
```

---

## 3. Visão de Interface (Contratos)

### 3.1 Endpoint Autenticado

```python
@router.get("/api/rotas/minha-rota")
async def minha_rota(user = Depends(get_current_user), db = Depends(get_db)):
    """Retorna a rota ativa do caminhão do motorista logado."""
    motorista = await db.execute(
        select(Motorista).where(Motorista.auth_id == user.id)
    )
    motorista = motorista.scalar_one_or_none()
    if not motorista or not motorista.caminhao_id:
        raise HTTPException(404, "Sem rota cadastrada")

    rota = await db.execute(
        select(Rota)
        .where(Rota.caminhao_id == motorista.caminhao_id, Rota.ativa == True)
        .options(selectinload(Rota.pontos))
    )
    rota = rota.scalar_one_or_none()
    if not rota:
        raise HTTPException(404, "Nenhuma rota ativa")

    return {
        "rota_id": rota.rota_id,
        "tipo_coleta": rota.tipo_coleta,
        "pontos": sorted([
            {
                "ordem": p.ordem,
                "endereco": p.endereco,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "horario_passagem": p.horario_passagem.strftime("%H:%M"),
            }
            for p in rota.pontos
        ], key=lambda x: x["ordem"])
    }
```

### 3.2 Ícones no Mapa

| Posição | Ícone | Cor |
|---|---|---|
| Primeiro ponto | `saco-de-lixo-start` | Verde |
| Último ponto | `saco-de-lixo-finish` | Vermelho |
| Intermediários | `saco-de-lixo` | Amarelo |
| Posição atual | `caminhao-de-reciclagem` | — |

---

## 4. Mapeamento SRS → SDD

| Requisito SRS | Componente SDD | Status |
|---|---|---|
| **RF-ROT1-01** — Carregar rota do caminhão logado | `GET /api/rotas/minha-rota` (JWT → motorista → caminhão → rota) | ✅ |
| **RF-ROT1-02** — Leaflet Routing Machine | `MapaRotaMotorista.svelte` | ✅ |
| **RF-ROT1-03** — Ícones diferenciados | 3 ícones por posição (início, fim, intermediário) | ✅ |
| **RF-ROT1-04** — Tabela colapsável | `TabelaPontosRota.svelte` com toggle | ✅ |
| **RF-ROT1-05** — Zoom ao clicar na tabela | `map.setView([lat, lng], 15)` + `openPopup()` | ✅ |
| **RF-ROT1-06** — Popup com horário | `bindPopup("Ponto N — Endereço — HH:MM")` | ✅ |

---

## 5. Decisões Arquiteturais

| # | Decisão | Justificativa |
|:-:|---------|---------------|
| 1 | Endpoint único `minha-rota` (sem truck_id no URL) | Segurança — motorista só acessa sua própria rota. truck_id extraído do JWT |
| 2 | `selectinload(Rota.pontos)` | Evita N+1 queries. Carrega tudo em 1 query |
