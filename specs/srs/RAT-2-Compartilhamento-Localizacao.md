# 📋 Especificação de Requisitos — RAT-2: Compartilhamento de Localização (Motorista)

> **Funcionalidade:** RAT-2 — Compartilhamento de Localização em Tempo Real
> **Módulo:** Rastreamento e Geolocalização
> **Versão:** 1.0
> **Referência:** IEEE 830 / ISO/IEC/IEEE 29148:2018

---

## 1. Introdução

### 1.1 Propósito

Permitir que o **motorista/coletor** autenticado compartilhe sua localização em tempo real com o sistema, enviando coordenadas GPS via **WebSocket** para o servidor FastAPI, que persiste no banco e retransmite para os cidadãos conectados. O motorista visualiza sua posição no mapa junto com a rota de coleta planejada.

### 1.2 Cenário de Negócio

> O motorista inicia seu turno, faz login e clica em "Iniciar Coleta". O GPS do dispositivo começa a enviar posição a cada 5 segundos via WebSocket. No mapa, ele vê sua localização atualizar junto com os pontos da rota que deve seguir. Ao final do turno, clica em "Encerrar Coleta" e a transmissão para.

---

## 2. Descrição Geral

### 2.1 Perspectiva do Produto

O compartilhamento de localização opera na **Área do Coletor** (`/coletor`):

1. **Botão "Iniciar Coleta"** ativa `watchPosition` e abre conexão WebSocket autenticada.
2. **Transmissão contínua** de coordenadas a cada 5 segundos.
3. **Persistência** das coordenadas no PostgreSQL via FastAPI (com geocodificação assíncrona).
4. **Retransmissão** para cidadãos conectados no WebSocket público.
5. **Botão "Encerrar Coleta"** para o GPS e fecha o WebSocket.

### 2.2 Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| **RF-RAT2-01** | O sistema deve exibir um botão "Iniciar Coleta" na Área do Coletor que ativa o compartilhamento de localização. |
| **RF-RAT2-02** | Ao iniciar, o sistema deve solicitar permissão de geolocalização e iniciar `watchPosition` com `enableHighAccuracy: true`. |
| **RF-RAT2-03** | O sistema deve estabelecer uma conexão WebSocket autenticada (JWT no header) com `ws://api/ws/driver/{truck_id}`. |
| **RF-RAT2-04** | O sistema deve enviar coordenadas (latitude, longitude, timestamp) via WebSocket a cada 5 segundos. |
| **RF-RAT2-05** | O servidor FastAPI deve persistir cada localização no PostgreSQL com: truck_id, latitude, longitude, endereço (geocodificado assincronamente), timestamp. |
| **RF-RAT2-06** | O servidor FastAPI deve geocodificar o endereço via Nominatim de forma **assíncrona** (não bloqueia o WebSocket) e cachear resultados no PostgreSQL. |
| **RF-RAT2-07** | O sistema deve exibir no mapa a posição atual do motorista com marcador de caminhão atualizado em tempo real. |
| **RF-RAT2-08** | O sistema deve exibir um card de informações com: nome do motorista, ID do veículo, endereço atual, e status (em coleta/parado). |
| **RF-RAT2-09** | O sistema deve exibir botão "Encerrar Coleta" que para o GPS, fecha o WebSocket e marca o caminhão como offline. |
| **RF-RAT2-10** | Se o GPS falhar ou o WebSocket desconectar, o sistema deve exibir alerta visual e tentar reconectar automaticamente. |

---

## 3. Entradas e Saídas

### 3.1 Entradas (Inputs)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Coordenadas GPS | `{lat, lng, timestamp}` | ✅ | Capturadas automaticamente a cada 5s via `watchPosition`. |
| JWT | String (header WS) | ✅ | Token de autenticação para conexão WebSocket. |

### 3.2 Saídas (Outputs)

| Cenário | Saída |
|---------|-------|
| **Coleta iniciada** | Marcador no mapa atualiza em tempo real. Card de informações preenchido. Status: "Em coleta". |
| **Coleta encerrada** | GPS parado. WebSocket fechado. Caminhão marcado como offline. Status: "Fora de serviço". |
| **GPS falha** | Alerta "Erro ao capturar localização. Verifique as configurações do GPS." |
| **WebSocket desconectado** | Alerta "Conexão perdida. Tentando reconectar..." + tentativa automática. |

---

## 4. Regras de Negócio e Restrições

- **RN-RAT2-01 (Autenticação):** Apenas motoristas autenticados com JWT válido podem enviar localização. Conexões WebSocket sem JWT válido são rejeitadas.
- **RN-RAT2-02 (Frequência):** Coordenadas são enviadas a cada 5 segundos. O servidor ignora atualizações com intervalo menor que 3 segundos (anti-spam).
- **RN-RAT2-03 (Geocodificação Assíncrona):** A conversão coordenadas → endereço é feita em background task (FastAPI background_tasks ou Celery). Não bloqueia o fluxo principal.
- **RN-RAT2-04 (Cache de Geocodificação):** Coordenadas dentro de um raio de 50m de uma coordenada já geocodificada reutilizam o endereço cacheado, evitando chamadas desnecessárias ao Nominatim.
- **RN-RAT2-05 (Alta Precisão):** `enableHighAccuracy: true` é obrigatório para garantir precisão de GPS (usando GPS real, não Wi-Fi).
- **RN-RAT2-06 (Persistência):** Cada ponto de localização é armazenado no PostgreSQL para histórico. Dados com mais de 30 dias podem ser compactados (agregados por minuto em vez de a cada 5s).

---

## 5. Casos de Uso

### UC-RAT-02: Compartilhar Localização em Tempo Real

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Motorista/Coletor |
| **Pré-condições** | Motorista autenticado com caminhão associado. GPS disponível no dispositivo. |
| **Fluxo principal** | 1. Motorista acessa `/coletor`. <br> 2. Clica em "Iniciar Coleta". <br> 3. Navegador solicita permissão de GPS. <br> 4. WebSocket autenticado é estabelecido. <br> 5. GPS envia coordenadas a cada 5s via WebSocket. <br> 6. Servidor persiste e retransmite para cidadãos. <br> 7. Ao final, motorista clica em "Encerrar Coleta". <br> 8. GPS para, WebSocket fecha, caminhão fica offline. |
| **Fluxo alternativo** | GPS negado → mensagem de erro. Coleta não pode iniciar sem GPS. |
| **Fluxo de exceção** | WebSocket cai → reconexão automática. GPS falha → alerta + retry. |
| **Pós-condições** | Localização registrada no banco. Cidadãos veem caminhão no mapa. |

---

## 6. Critérios de Aceite

| ID | Critério | Formato Given-When-Then |
|:--:|---------|------------------------|
| CA-RAT2-01 | Início de coleta | **Dado que** o motorista está autenticado na Área do Coletor, **quando** clica em "Iniciar Coleta" e permite GPS, **então** o WebSocket conecta e o marcador do caminhão aparece no mapa em menos de 3 segundos. |
| CA-RAT2-02 | Transmissão contínua | **Dado que** a coleta foi iniciada, **quando** o motorista se move, **então** novas coordenadas são enviadas a cada 5 segundos e os cidadãos veem o marcador se mover. |
| CA-RAT2-03 | Geocodificação assíncrona | **Dado que** uma nova coordenada é recebida pelo servidor, **quando** é persistida, **então** o endereço é geocodificado em background em menos de 2 segundos, sem bloquear o WebSocket. |
| CA-RAT2-04 | Encerramento de coleta | **Dado que** o motorista clica em "Encerrar Coleta", **quando** o sistema processa, **então** o GPS para, o WebSocket fecha, e o caminhão é marcado como offline para os cidadãos. |
| CA-RAT2-05 | Reconexão automática | **Dado que** o WebSocket caiu por instabilidade de rede, **quando** a rede retorna, **então** o sistema reconecta em até 5 segundos e retoma a transmissão sem intervenção do motorista. |
