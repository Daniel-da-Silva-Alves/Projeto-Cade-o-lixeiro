# 📋 Especificação de Requisitos — NOT-1: Notificações Push

> **Funcionalidade:** NOT-1 — Notificações Push para Cidadão
> **Módulo:** Comunicação e Alertas
> **Versão:** 1.0
> **Referência:** IEEE 830 / ISO/IEC/IEEE 29148:2018

---

## 1. Introdução

### 1.1 Propósito

Notificar o cidadão quando um **caminhão de coleta está se aproximando** do seu bairro, usando a **Web Push API** (Service Worker). O cidadão se inscreve para receber notificações de bairros específicos, e o backend dispara a notificação quando o rastreamento WebSocket detecta que o caminhão entrou no raio do bairro cadastrado.

### 1.2 Cenário de Negócio

> O cidadão ativou notificações para o bairro "Flores". O caminhão de coleta orgânica entrou no bairro vizinho. Quando cruza a divisa para Flores, o cidadão recebe uma notificação no celular: "🚛 O caminhão de coleta orgânica está chegando em Flores!". Ele tem tempo de preparar o lixo.

---

## 2. Descrição Geral

### 2.1 Perspectiva do Produto

O sistema de notificações opera em três camadas:

1. **Frontend (Service Worker):** Registra subscription da Web Push API e exibe notificações.
2. **Backend (FastAPI):** Gerencia subscriptions e dispara pushes quando caminhão entra em bairro.
3. **Trigger:** Baseado na localização do caminhão (WebSocket de rastreamento) cruzada com polígonos de bairros (PostGIS).

### 2.2 Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| **RF-NOT1-01** | O sistema deve exibir botão "Ativar notificação" na página de Horários de Passagem, associado a cada bairro. |
| **RF-NOT1-02** | Ao clicar, o sistema deve solicitar permissão do navegador para notificações push via Web Push API. |
| **RF-NOT1-03** | O sistema deve registrar a subscription (endpoint + chaves) no PostgreSQL, associada ao bairro selecionado. |
| **RF-NOT1-04** | O sistema deve disparar notificação push quando o rastreamento WebSocket detectar que um caminhão entrou no polígono geográfico do bairro (via PostGIS `ST_Contains`). |
| **RF-NOT1-05** | A notificação deve conter: ícone do app, título "Cadê o Lixeiro?", mensagem "O caminhão de coleta [tipo] está chegando em [bairro]!". |
| **RF-NOT1-06** | O sistema deve permitir que o cidadão **desative** notificações para um bairro. |
| **RF-NOT1-07** | O sistema deve evitar notificações duplicadas: máximo 1 notificação por bairro por caminhão por hora. |

---

## 3. Entradas e Saídas

### 3.1 Entradas (Inputs)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `bairro` | String | ✅ | Bairro para receber notificação. |
| `subscription` | PushSubscription (Web Push API) | ✅ | Objeto de subscription do navegador (endpoint, keys). |

### 3.2 Saídas (Outputs)

| Cenário | Saída |
|---------|-------|
| **Notificação ativada** | Toast "Notificação ativada para [bairro]!" |
| **Push disparado** | Notificação do navegador/SO: "O caminhão está chegando em [bairro]!" |
| **Permissão negada** | Mensagem com instruções para habilitar nas configurações do navegador. |
| **Navegador incompatível** | Botão de notificação oculto. |

---

## 4. Regras de Negócio e Restrições

- **RN-NOT-01 (Sem Login):** Notificações são vinculadas ao dispositivo/navegador (subscription), não a uma conta de usuário.
- **RN-NOT-02 (Anti-Spam):** Máximo 1 push por bairro por caminhão por hora.
- **RN-NOT-03 (Trigger Geográfico):** A notificação é disparada quando `ST_Contains(bairro.geometry, POINT(truck.lng, truck.lat))` retorna `true` pela primeira vez na janela de 1 hora.
- **RN-NOT-04 (VAPID Keys):** Chaves VAPID (Voluntary Application Server Identification) devem ser configuradas no FastAPI para autenticar os pushes.
- **RN-NOT-05 (Limpeza):** Subscriptions que retornam erro 410 (Gone) devem ser removidas automaticamente do banco.

---

## 5. Casos de Uso

### UC-NOT-01: Ativar Notificação Push

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Cidadão |
| **Pré-condições** | Navegador compatível com Web Push API. |
| **Fluxo principal** | 1. Cidadão acessa `/horarios`. <br> 2. Clica em "Ativar notificação" para o bairro desejado. <br> 3. Navegador solicita permissão. <br> 4. Se concedida, sistema registra subscription + bairro no banco. <br> 5. Confirmação via toast. |
| **Fluxo alternativo** | Permissão negada → mensagem com instruções. |
| **Fluxo de exceção** | Navegador incompatível → botão oculto. |
| **Pós-condições** | Subscription registrada. Cidadão será notificado. |

---

## 6. Critérios de Aceite

| ID | Critério | Formato Given-When-Then |
|:--:|---------|------------------------|
| CA-NOT-01 | Ativação | **Dado que** o cidadão está em `/horarios` e o navegador suporta push, **quando** clica "Ativar notificação" para "Flores" e concede permissão, **então** a subscription é registrada e toast confirma. |
| CA-NOT-02 | Disparo de push | **Dado que** o cidadão ativou notificação para "Flores", **quando** o caminhão de coleta orgânica entra no bairro Flores (detectado via PostGIS), **então** o cidadão recebe push "O caminhão de coleta orgânica está chegando em Flores!" em menos de 10 segundos. |
| CA-NOT-03 | Anti-spam | **Dado que** o push já foi enviado para "Flores" há 30 minutos pelo mesmo caminhão, **quando** o caminhão sai e re-entra no bairro, **então** nenhum novo push é enviado (janela de 1h). |
| CA-NOT-04 | Desativação | **Dado que** o cidadão ativou notificação para "Centro", **quando** clica em "Desativar notificação", **então** a subscription é removida e nenhum push futuro é enviado para "Centro". |
