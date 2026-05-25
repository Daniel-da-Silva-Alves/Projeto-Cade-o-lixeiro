# 📋 Especificação de Requisitos — GAM-1: Ranking de Bairros

> **Funcionalidade:** GAM-1 — Ranking de Sustentabilidade por Bairro
> **Módulo:** Gamificação e Engajamento
> **Versão:** 1.0
> **Referência:** IEEE 830 / ISO/IEC/IEEE 29148:2018

---

## 1. Introdução

### 1.1 Propósito

Promover a **competição saudável entre bairros** de Manaus em práticas sustentáveis. O ranking calcula uma pontuação de sustentabilidade para cada bairro com base em dois critérios: volume de **denúncias resolvidas** e quantidade de **descartes corretos** registrados. O objetivo é gamificar a participação cidadã e incentivar bairros a serem mais ativos na gestão de resíduos.

### 1.2 Cenário de Negócio

> O cidadão acessa a página de Ranking e vê que seu bairro "Cachoeirinha" está em 5º lugar no ranking mensal. Ele decide fazer mais denúncias e descartes corretos para subir no ranking. Na página inicial, um widget mostra os Top 3 bairros do mês com destaque visual.

---

## 2. Descrição Geral

### 2.1 Perspectiva do Produto

O sistema de Ranking possui dois componentes:

1. **Página dedicada** (`/ranking`) com tabela/gráfico de todos os bairros, filtros por período e critério.
2. **Widget na página inicial** com os Top 3 bairros do mês atual.

A pontuação é calculada via **View Materializada** no PostgreSQL, atualizada periodicamente (a cada hora) para não impactar performance.

### 2.2 Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| **RF-GAM1-01** | O sistema deve exibir uma página `/ranking` com o ranking completo de todos os bairros, ordenado por pontuação decrescente. |
| **RF-GAM1-02** | O ranking deve calcular pontuação com base em: denúncias resolvidas no bairro (peso 2) + descartes corretos registrados (peso 1). |
| **RF-GAM1-03** | O sistema deve permitir filtrar o ranking por **período**: mensal (mês atual) ou acumulado (histórico total). |
| **RF-GAM1-04** | O sistema deve exibir para cada bairro: posição, nome do bairro, pontuação total, quantidade de denúncias resolvidas, quantidade de descartes corretos, e variação em relação ao mês anterior (↑ ↓ →). |
| **RF-GAM1-05** | O sistema deve exibir um **widget/badge na página inicial** com os Top 3 bairros do mês, incluindo posição, nome e pontuação. |
| **RF-GAM1-06** | O sistema deve atualizar o ranking automaticamente a cada hora via View Materializada no PostgreSQL. |
| **RF-GAM1-07** | O sistema deve exibir **gráficos visuais** (barras ou radar) comparando os Top 10 bairros. |

---

## 3. Entradas e Saídas

### 3.1 Entradas (Inputs)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `periodo` | Enum (`mensal`, `acumulado`) | ❌ | Filtro de período. Padrão: `mensal`. |

### 3.2 Saídas (Outputs)

| Cenário | Saída |
|---------|-------|
| **Ranking mensal** | Tabela com todos os bairros ordenados por pontuação do mês corrente + gráfico Top 10. |
| **Ranking acumulado** | Tabela com todos os bairros ordenados por pontuação histórica total + gráfico Top 10. |
| **Widget Home (Top 3)** | Card compacto com 1º, 2º e 3º lugar + medalhas visuais (🥇🥈🥉). |

---

## 4. Regras de Negócio e Restrições

- **RN-GAM-01 (Acesso Público):** O ranking é público, sem necessidade de autenticação.
- **RN-GAM-02 (Cálculo de Pontuação):** `pontuacao = (denuncias_resolvidas × 2) + (descartes_corretos × 1)`. Denúncias resolvidas têm peso maior por envolverem mais esforço coletivo.
- **RN-GAM-03 (Período Mensal):** O ranking mensal considera dados do 1º ao último dia do mês corrente. É resetado automaticamente no início de cada mês.
- **RN-GAM-04 (Período Acumulado):** O ranking acumulado considera todo o histórico desde o lançamento da plataforma.
- **RN-GAM-05 (Atualização):** A View Materializada é atualizada a cada hora via job agendado (pg_cron ou FastAPI scheduler). Não é recalculada a cada request.
- **RN-GAM-06 (Variação):** A variação (↑ ↓ →) é calculada comparando a posição atual com a posição no mês anterior.

---

## 5. Casos de Uso

### UC-GAM-01: Consultar Ranking de Bairros

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Cidadão |
| **Pré-condições** | Nenhuma (acesso público). |
| **Fluxo principal** | 1. Cidadão acessa `/ranking`. <br> 2. Sistema exibe ranking mensal por padrão. <br> 3. Cidadão visualiza tabela + gráfico. <br> 4. Opcionalmente alterna para ranking acumulado. |
| **Fluxo alternativo** | Cidadão vê widget Top 3 na página inicial e clica para ver ranking completo. |
| **Fluxo de exceção** | Sem dados suficientes → exibir mensagem "Ranking em construção. Contribua com denúncias e descartes!" |
| **Pós-condições** | Ranking exibido com dados atualizados (última atualização ≤ 1 hora). |

---

## 6. Critérios de Aceite

| ID | Critério | Formato Given-When-Then |
|:--:|---------|------------------------|
| CA-GAM-01 | Ranking mensal | **Dado que** estamos em maio/2026, **quando** o cidadão acessa `/ranking` com filtro "Mensal", **então** a tabela exibe bairros ordenados pela pontuação de maio/2026. |
| CA-GAM-02 | Ranking acumulado | **Dado que** o cidadão seleciona filtro "Acumulado", **quando** a tabela carrega, **então** exibe bairros ordenados pela pontuação histórica total. |
| CA-GAM-03 | Widget Top 3 | **Dado que** o cidadão está na página inicial, **quando** a página carrega, **então** o widget exibe os 3 bairros com maior pontuação no mês com medalhas visuais (🥇🥈🥉). |
| CA-GAM-04 | Variação de posição | **Dado que** o bairro "Flores" estava em 5º lugar em abril e agora está em 3º em maio, **quando** o ranking mensal de maio é exibido, **então** "Flores" aparece com indicador ↑2 (subiu 2 posições). |
| CA-GAM-05 | Atualização automática | **Dado que** uma nova denúncia foi resolvida no bairro "Centro", **quando** a View Materializada é atualizada (a cada hora), **então** a pontuação do "Centro" reflete a denúncia resolvida no próximo refresh da página. |
