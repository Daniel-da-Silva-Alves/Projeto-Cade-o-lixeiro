# 📋 Especificação de Requisitos — RAT-1: Rastreamento de Caminhões (Cidadão)

> **Funcionalidade:** RAT-1 — Rastreamento em Tempo Real (Visão do Cidadão)
> **Módulo:** Rastreamento e Geolocalização
> **Versão:** 1.0
> **Referência:** IEEE 830 / ISO/IEC/IEEE 29148:2018

---

## 1. Introdução

### 1.1 Propósito

Exibir a **localização em tempo real dos caminhões de coleta** no mapa interativo da página inicial, permitindo que o cidadão saiba exatamente onde o caminhão está e se está se aproximando do seu bairro. A atualização é instantânea via **WebSocket**, eliminando a necessidade de refresh manual.

### 1.2 Cenário de Negócio

> O cidadão ouve o barulho de um caminhão de coleta na rua vizinha. Abre o app e vê no mapa que o caminhão está a 2 quadras de distância, se movendo em direção à sua rua. Ele tem tempo de descer com os sacos de lixo antes que o caminhão passe.

---

## 2. Descrição Geral

### 2.1 Perspectiva do Produto

A página inicial (`/`) exibe um mapa com:

1. **Localização do cidadão** (marcador azul, via Geolocation API).
2. **Caminhões ativos** (marcadores verdes, atualizados em tempo real via WebSocket).
3. **Filtro por bairro** para mostrar apenas caminhões relevantes.
4. **Legenda lateral** com lista de caminhões ativos e última atualização.

A conexão WebSocket é estabelecida ao abrir a página e mantida enquanto o usuário estiver ativo.

### 2.2 Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| **RF-RAT1-01** | O sistema deve exibir um mapa interativo (Leaflet.js) centralizado na localização do cidadão (se GPS permitido) ou em Manaus (fallback). |
| **RF-RAT1-02** | O sistema deve estabelecer uma conexão WebSocket com o servidor FastAPI para receber atualizações de localização dos caminhões em tempo real. |
| **RF-RAT1-03** | O sistema deve exibir marcadores de caminhão no mapa que se movem automaticamente conforme novas coordenadas chegam via WebSocket. |
| **RF-RAT1-04** | O sistema deve exibir um popup ao clicar no marcador do caminhão com: ID do caminhão, endereço atual, última atualização, e status (em rota/parado). |
| **RF-RAT1-05** | O sistema deve permitir filtrar caminhões por bairro via dropdown dinâmico (carregado da API `/api/bairros`). |
| **RF-RAT1-06** | O sistema deve exibir um card de legenda lateral com lista de caminhões ativos visíveis no mapa, com ID e timestamp da última atualização. |
| **RF-RAT1-07** | O sistema deve detectar a localização do cidadão via Geolocation API e exibir marcador no mapa. |
| **RF-RAT1-08** | Quando não houver caminhões ativos no bairro filtrado, o sistema deve exibir mensagem "Nenhum caminhão ativo no bairro selecionado". |
| **RF-RAT1-09** | O sistema deve exibir indicador visual de conexão WebSocket (online/offline) no canto da tela. |

---

## 3. Entradas e Saídas

### 3.1 Entradas (Inputs)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `bairro` | String (dropdown) | ❌ | Filtro de bairro. Padrão: "Todos os bairros". |
| GPS do cidadão | Coordenadas (lat, lng) | ❌ | Localização automática via browser. |

### 3.2 Saídas (Outputs)

| Cenário | Saída |
|---------|-------|
| **WebSocket conectado + caminhões ativos** | Mapa com marcadores de caminhões atualizando em tempo real + legenda. |
| **WebSocket conectado + sem caminhões** | Mapa com localização do cidadão + mensagem "Nenhum caminhão ativo". |
| **WebSocket desconectado** | Indicador "Offline" + última posição conhecida dos caminhões (congelada). |
| **GPS negado** | Mapa centralizado em Manaus. Funcionalidade de filtro por bairro ainda funcional. |

---

## 4. Regras de Negócio e Restrições

- **RN-RAT1-01 (Acesso Público):** O rastreamento é público, sem necessidade de autenticação.
- **RN-RAT1-02 (WebSocket):** A conexão WebSocket é feita com o endpoint FastAPI `ws://api/ws/tracking`. O servidor broadcast posições de todos os caminhões ativos a cada nova atualização recebida de um motorista.
- **RN-RAT1-03 (Filtro Local):** O filtro por bairro é aplicado no frontend sobre os dados recebidos via WebSocket, sem nova requisição ao servidor.
- **RN-RAT1-04 (Timeout de Atividade):** Um caminhão é considerado "inativo" se não enviar atualização por mais de 5 minutos. Seu marcador deve mudar de cor (verde → cinza) e exibir status "Parado".
- **RN-RAT1-05 (Reconexão):** Se a conexão WebSocket cair, o frontend deve tentar reconectar automaticamente a cada 5 segundos, até 10 tentativas. Após isso, exibir mensagem de erro.
- **RN-RAT1-06 (Performance):** O frontend deve usar throttle de 1s para animação de movimento dos marcadores, evitando re-renders excessivos.

---

## 5. Casos de Uso

### UC-RAT-01: Rastrear Caminhões em Tempo Real

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Cidadão |
| **Pré-condições** | Pelo menos um caminhão ativo com motorista compartilhando localização. |
| **Fluxo principal** | 1. Cidadão acessa `/` (página inicial). <br> 2. Sistema solicita permissão de GPS. <br> 3. Conexão WebSocket estabelecida. <br> 4. Marcadores de caminhões aparecem no mapa e se movem em tempo real. <br> 5. Cidadão filtra por bairro se desejar. <br> 6. Cidadão clica em marcador para ver detalhes. |
| **Fluxo alternativo** | GPS negado → mapa centrado em Manaus, filtro manual por bairro. |
| **Fluxo de exceção** | WebSocket falha → modo offline com última posição conhecida. |
| **Pós-condições** | Cidadão visualiza posições atualizadas dos caminhões. |

---

## 6. Critérios de Aceite

| ID | Critério | Formato Given-When-Then |
|:--:|---------|------------------------|
| CA-RAT1-01 | Atualização em tempo real | **Dado que** o cidadão está na página inicial com WebSocket ativo, **quando** um motorista envia nova localização, **então** o marcador do caminhão no mapa se move para a nova posição em menos de 1 segundo. |
| CA-RAT1-02 | Filtro por bairro | **Dado que** existem 3 caminhões ativos (1 no Centro, 2 em Flores), **quando** o cidadão seleciona "Centro" no filtro, **então** apenas 1 marcador é visível no mapa. |
| CA-RAT1-03 | Caminhão inativo | **Dado que** o caminhão "CAM-001" não envia atualização há 6 minutos, **quando** o mapa é verificado, **então** o marcador de "CAM-001" aparece cinza com status "Parado". |
| CA-RAT1-04 | Reconexão automática | **Dado que** a conexão WebSocket foi perdida, **quando** a rede volta, **então** o sistema reconecta automaticamente e os marcadores voltam a atualizar sem refresh manual. |
| CA-RAT1-05 | Indicador de conexão | **Dado que** o WebSocket está desconectado, **quando** o cidadão olha o canto da tela, **então** vê indicador vermelho "Offline" pulsando. |
