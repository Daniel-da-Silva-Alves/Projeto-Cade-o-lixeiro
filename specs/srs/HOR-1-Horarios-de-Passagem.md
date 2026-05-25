# 📋 Especificação de Requisitos — HOR-1: Horários de Passagem

> **Funcionalidade:** HOR-1 — Consulta de Horários de Passagem
> **Módulo:** Rotas e Coleta
> **Versão:** 1.0
> **Referência:** IEEE 830 / ISO/IEC/IEEE 29148:2018

---

## 1. Introdução

### 1.1 Propósito

Permitir que o cidadão consulte os **horários e dias de passagem** dos caminhões de coleta em seus bairros, visualizando a rota no mapa, o tipo de coleta (orgânico, reciclável, etc.) e os horários reais de cada ponto da rota. Além disso, possibilita ao cidadão receber **notificações push** quando o caminhão estiver próximo ao seu bairro.

### 1.2 Cenário de Negócio

> O cidadão quer saber quando o caminhão de coleta seletiva passa no seu bairro. Acessa "Horários de Passagem", seleciona seu bairro e vê: Segunda e Quinta, 14h-16h, Coleta Reciclável. No mapa, visualiza a rota que o caminhão fará. Ativa a notificação para ser avisado quando o caminhão estiver chegando.

---

## 2. Descrição Geral

### 2.1 Perspectiva do Produto

A página de Horários de Passagem (`/horarios`) oferece:

1. **Seleção de bairro(s)** via chips de seleção múltipla ou dropdown.
2. **Tabela de rotas** com horários reais de passagem, dias da semana e tipo de coleta.
3. **Visualização da rota no mapa** com Leaflet.js + Routing Machine.
4. **Cadastro de notificação push** para aviso quando o caminhão se aproximar.

### 2.2 Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| **RF-HOR1-01** | O sistema deve exibir a lista de bairros como chips de seleção múltipla, carregados dinamicamente da API `/api/bairros`. |
| **RF-HOR1-02** | Ao selecionar bairro(s), o sistema deve buscar e exibir as rotas de coleta associadas em uma tabela com: ID da rota, tipo de coleta, dias da semana, horário de início e fim, endereço inicial e final. |
| **RF-HOR1-03** | O sistema deve exibir o **horário real de passagem** (`passage_time`) de cada ponto da rota, não apenas os endereços. |
| **RF-HOR1-04** | O sistema deve exibir os **dias da semana** em que cada rota opera (ex: Seg, Qua, Sex). |
| **RF-HOR1-05** | O sistema deve exibir o **tipo de coleta** de cada rota (orgânico, reciclável, perigoso, etc.). |
| **RF-HOR1-06** | Ao clicar em uma rota na tabela, o sistema deve renderizar a rota completa no mapa com Leaflet Routing Machine, mostrando waypoints com horários. |
| **RF-HOR1-07** | O sistema deve oferecer opção de **ativar notificação push** para um bairro/rota, notificando quando o caminhão estiver próximo. |
| **RF-HOR1-08** | Quando nenhuma rota for encontrada para os bairros selecionados, o sistema deve exibir mensagem "Nenhuma rota de coleta encontrada para o(s) bairro(s) selecionado(s)". |

---

## 3. Entradas e Saídas

### 3.1 Entradas (Inputs)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `bairros` | Array de strings (chips) | ✅ | Bairro(s) selecionado(s) pelo cidadão. |
| `notificacao.bairro` | String | ✅* | Bairro para receber notificação. *Obrigatório apenas ao ativar notificação. |

### 3.2 Saídas (Outputs)

| Cenário | Saída |
|---------|-------|
| **Bairros selecionados — com rotas** | Tabela com rotas + mapa com rota desenhada ao clicar. |
| **Bairros selecionados — sem rotas** | Mensagem informativa. |
| **Rota clicada na tabela** | Mapa renderiza a rota com waypoints, horários e ícones. |
| **Notificação ativada** | Toast de confirmação "Você será notificado quando o caminhão se aproximar de [bairro]". |

---

## 4. Regras de Negócio e Restrições

- **RN-HOR-01 (Acesso Público):** A consulta de horários é pública, sem necessidade de autenticação.
- **RN-HOR-02 (Seleção Múltipla):** O cidadão pode selecionar múltiplos bairros simultaneamente. As rotas de todos os bairros selecionados são exibidas.
- **RN-HOR-03 (Tipos de Coleta):** Os tipos de coleta são: `organico`, `reciclavel`, `perigoso`, `verde`, `geral`. Cada rota tem um tipo associado.
- **RN-HOR-04 (Dias da Semana):** Cada rota possui um campo de dias da semana (bitfield ou array: `[seg, qua, sex]`).
- **RN-HOR-05 (Notificação Push):** Notificações push utilizam a Web Push API (Service Worker). O sistema envia notificação quando a localização do caminhão (via WebSocket) entrar no raio do bairro cadastrado.
- **RN-HOR-06 (Horários):** O campo `passage_time` de `RouteLocation` é obrigatório e deve ser exibido em formato HH:MM.

---

## 5. Casos de Uso

### UC-HOR-01: Consultar Horários de Passagem

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Cidadão |
| **Pré-condições** | Nenhuma (acesso público). |
| **Fluxo principal** | 1. Cidadão acessa `/horarios`. <br> 2. Seleciona um ou mais bairros via chips. <br> 3. Sistema busca rotas via `POST /api/rotas/por-bairro`. <br> 4. Tabela é preenchida com rotas (tipo, dias, horários). <br> 5. Cidadão clica em uma rota. <br> 6. Mapa renderiza a rota com waypoints e horários. |
| **Fluxo alternativo** | Sem rotas → mensagem informativa. |
| **Fluxo de exceção** | API indisponível → mensagem de erro. |
| **Pós-condições** | Rotas exibidas na tabela e/ou mapa. |

### UC-HOR-02: Ativar Notificação Push

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Cidadão |
| **Pré-condições** | Navegador compatível com Web Push API. |
| **Fluxo principal** | 1. Cidadão visualiza rotas do seu bairro. <br> 2. Clica em "Ativar notificação". <br> 3. Navegador solicita permissão para notificações. <br> 4. Se concedida, sistema registra o subscription. <br> 5. Quando caminhão da rota entrar no bairro, push é enviado. |
| **Fluxo alternativo** | Permissão negada → mensagem explicando como habilitar nas configurações do navegador. |
| **Fluxo de exceção** | Navegador incompatível → botão de notificação oculto. |
| **Pós-condições** | Subscription registrado. Cidadão será notificado quando caminhão se aproximar. |

---

## 6. Critérios de Aceite

| ID | Critério | Formato Given-When-Then |
|:--:|---------|------------------------|
| CA-HOR-01 | Seleção de bairro | **Dado que** o cidadão seleciona o chip "Cachoeirinha", **quando** as rotas carregam, **então** a tabela exibe todas as rotas que passam por Cachoeirinha com tipo de coleta, dias e horários. |
| CA-HOR-02 | Seleção múltipla | **Dado que** o cidadão seleciona "Centro" e "Flores", **quando** as rotas carregam, **então** a tabela exibe rotas de ambos os bairros. |
| CA-HOR-03 | Rota no mapa | **Dado que** a tabela exibe rotas, **quando** o cidadão clica em uma rota, **então** o mapa renderiza a rota completa com waypoints marcados e horários de passagem em cada ponto. |
| CA-HOR-04 | Horário de passagem | **Dado que** uma rota possui 5 pontos, **quando** exibida na tabela/mapa, **então** cada ponto mostra o horário estimado de passagem (ex: "Ponto 1: Rua X — 14:30"). |
| CA-HOR-05 | Notificação push | **Dado que** o cidadão ativou notificação para o bairro "Flores", **quando** o caminhão da rota entra no bairro Flores (via rastreamento WebSocket), **então** o cidadão recebe uma notificação push "O caminhão de coleta está chegando no seu bairro!". |
