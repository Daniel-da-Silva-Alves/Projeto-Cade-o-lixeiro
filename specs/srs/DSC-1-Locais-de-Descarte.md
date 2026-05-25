# 📋 Especificação de Requisitos — DSC-1: Locais de Descarte

> **Funcionalidade:** DSC-1 — Consulta de Locais de Descarte Consciente
> **Módulo:** Descarte e Sustentabilidade
> **Versão:** 1.0
> **Referência:** IEEE 830 / ISO/IEC/IEEE 29148:2018

---

## 1. Introdução

### 1.1 Propósito

Permitir que o cidadão consulte **pontos de descarte consciente** na cidade de Manaus, filtrando por bairro, tipo de resíduo, ou nome/endereço do local. A funcionalidade exibe os resultados em um mapa interativo (Leaflet.js) e mostra informações detalhadas de cada ponto, incluindo horário de funcionamento e avaliações de outros usuários.

### 1.2 Cenário de Negócio

> O cidadão tem equipamentos eletrônicos antigos e quer descartar corretamente. Abre o app, acessa "Locais de Descarte", filtra por "Eletrônicos" e encontra os pontos de coleta mais próximos com horários de funcionamento e avaliações de outros cidadãos.

---

## 2. Descrição Geral

### 2.1 Perspectiva do Produto

A página de Locais de Descarte (`/descarte`) é uma interface pública (sem login) que integra:

1. **Mapa interativo** com marcadores para cada local de descarte.
2. **Painel de filtros** com opções de bairro, tipo de resíduo e busca textual.
3. **Detecção automática** do bairro do usuário via GPS (com permissão).
4. **Cards de detalhes** com informações do local, horários e avaliações.

### 2.2 Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| **RF-DSC1-01** | O sistema deve exibir um mapa interativo (Leaflet.js) centralizado em Manaus com marcadores para cada local de descarte cadastrado. |
| **RF-DSC1-02** | O sistema deve permitir filtrar locais de descarte por **bairro** via dropdown dinâmico (dados carregados da API `/api/bairros`). |
| **RF-DSC1-03** | O sistema deve permitir filtrar locais de descarte por **tipo de resíduo** (orgânico, reciclável, eletrônico, perigoso, construção, têxtil, verde, não reciclável, óleo, outros). |
| **RF-DSC1-04** | O sistema deve permitir **busca textual** por nome ou endereço do local de descarte. |
| **RF-DSC1-05** | O sistema deve oferecer **detecção automática do bairro** do cidadão via Geolocation API, pré-selecionando o filtro de bairro com o resultado. |
| **RF-DSC1-06** | Ao clicar em um marcador no mapa, o sistema deve exibir um popup/card com: nome do local, endereço, tipos de resíduo aceitos, horário de funcionamento e avaliação média. |
| **RF-DSC1-07** | O sistema deve permitir que usuários enviem **avaliações** (1-5 estrelas) e **comentários** sobre um local de descarte, sem necessidade de login (anônimo). |
| **RF-DSC1-08** | O sistema deve ajustar automaticamente o zoom do mapa para exibir todos os marcadores filtrados (`fitBounds`). |
| **RF-DSC1-09** | Quando nenhum resultado for encontrado, o sistema deve exibir mensagem informativa "Nenhum local de descarte encontrado para os filtros selecionados". |

---

## 3. Entradas e Saídas

### 3.1 Entradas (Inputs)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `bairro` | String (dropdown) | ❌ | Bairro selecionado pelo usuário ou detectado via GPS. |
| `tipo_residuo` | String (dropdown) | ❌ | Tipo de resíduo aceito no local. |
| `busca` | String (texto livre) | ❌ | Termo de busca por nome ou endereço. |
| `avaliacao.estrelas` | Integer (1-5) | ✅* | Nota do usuário para o local. *Obrigatório apenas ao avaliar. |
| `avaliacao.comentario` | String (textarea) | ❌ | Comentário textual sobre o local. |

### 3.2 Saídas (Outputs)

| Cenário | Saída |
|---------|-------|
| **Filtros aplicados — com resultados** | Mapa com marcadores posicionados + popup com detalhes ao clicar. |
| **Filtros aplicados — sem resultados** | Mensagem informativa + mapa vazio centralizado em Manaus. |
| **Detecção GPS — sucesso** | Bairro pré-selecionado no dropdown + filtro aplicado automaticamente. |
| **Detecção GPS — negada/falha** | Dropdown sem pré-seleção. Usuário seleciona manualmente. |
| **Avaliação enviada** | Toast de confirmação + média atualizada no card do local. |

---

## 4. Regras de Negócio e Restrições

- **RN-DSC-01 (Acesso Público):** A consulta de locais de descarte não requer autenticação.
- **RN-DSC-02 (Filtros Combinados):** Os filtros de bairro, tipo de resíduo e busca textual devem ser combinados com operador AND (interseção).
- **RN-DSC-03 (Avaliação Anônima):** Avaliações são anônimas. Para evitar spam, implementar rate limiting por IP (máx. 1 avaliação por local por IP a cada 24h).
- **RN-DSC-04 (Tipos de Resíduo):** Os tipos de resíduo aceitos são: `organic`, `recyclables`, `electronics`, `hazardous`, `construction`, `textile`, `green`, `non_recyclable`, `oil`, `other`.
- **RN-DSC-05 (Bairros Dinâmicos):** A lista de bairros é carregada dinamicamente da tabela `bairros` no PostgreSQL via endpoint `/api/bairros`.
- **RN-DSC-06 (Horário de Funcionamento):** Cada local de descarte deve possuir campos de horário de abertura e fechamento por dia da semana.

---

## 5. Casos de Uso

### UC-DSC-01: Consultar Locais de Descarte

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Cidadão |
| **Pré-condições** | Nenhuma (acesso público). |
| **Fluxo principal** | 1. Cidadão acessa `/descarte` via menu. <br> 2. Sistema solicita permissão de geolocalização. <br> 3. Se concedida, pré-seleciona o bairro detectado. <br> 4. Cidadão opcionalmente ajusta filtros (bairro, tipo, busca). <br> 5. Sistema exibe marcadores no mapa com os locais filtrados. <br> 6. Cidadão clica em marcador e visualiza detalhes. |
| **Fluxo alternativo** | GPS negado → usuário seleciona bairro manualmente. |
| **Fluxo de exceção** | API indisponível → exibir mensagem de erro e mapa vazio. |
| **Pós-condições** | Locais de descarte exibidos no mapa com detalhes acessíveis. |

### UC-DSC-02: Avaliar Local de Descarte

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Cidadão |
| **Pré-condições** | Local de descarte visível no mapa/card. |
| **Fluxo principal** | 1. Cidadão clica no marcador/card de um local. <br> 2. Visualiza detalhes e avaliações existentes. <br> 3. Seleciona nota (1-5 estrelas). <br> 4. Opcionalmente digita comentário. <br> 5. Clica em "Enviar avaliação". <br> 6. Sistema registra e atualiza a média. |
| **Fluxo alternativo** | — |
| **Fluxo de exceção** | Rate limit atingido → mensagem "Você já avaliou este local hoje." |
| **Pós-condições** | Avaliação registrada. Média atualizada. |

---

## 6. Critérios de Aceite

| ID | Critério | Formato Given-When-Then |
|:--:|---------|------------------------|
| CA-DSC-01 | Filtro por bairro | **Dado que** o cidadão seleciona "Cachoeirinha" no filtro de bairros, **quando** os resultados carregam, **então** apenas locais de descarte do bairro Cachoeirinha são exibidos no mapa. |
| CA-DSC-02 | Filtro por tipo de resíduo | **Dado que** o cidadão seleciona "Eletrônicos" no filtro de tipo, **quando** os resultados carregam, **então** apenas locais que aceitam resíduos eletrônicos são exibidos. |
| CA-DSC-03 | Filtros combinados | **Dado que** o cidadão seleciona bairro "Centro" e tipo "Recicláveis", **quando** os resultados carregam, **então** apenas locais do Centro que aceitam recicláveis são exibidos. |
| CA-DSC-04 | Detecção GPS | **Dado que** o cidadão permitiu geolocalização e está no bairro "Flores", **quando** a página carrega, **então** o dropdown de bairro é pré-selecionado com "Flores" e os resultados são filtrados automaticamente. |
| CA-DSC-05 | Avaliação com rate limit | **Dado que** o cidadão já avaliou o local "Ecoponto Centro" nas últimas 24h, **quando** tenta enviar nova avaliação, **então** o sistema rejeita com mensagem "Você já avaliou este local hoje." |
| CA-DSC-06 | Horário de funcionamento | **Dado que** o cidadão clica no marcador de um local de descarte, **quando** o card/popup abre, **então** exibe os horários de funcionamento do local para cada dia da semana. |
