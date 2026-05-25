# 📋 Especificação de Requisitos — AUT-2: Logout

> **Funcionalidade:** AUT-2 — Logout do Motorista
> **Módulo:** Autenticação e Gestão de Usuários
> **Versão:** 1.0
> **Referência:** IEEE 830 / ISO/IEC/IEEE 29148:2018

---

## 1. Introdução

### 1.1 Propósito

Permitir que o **Motorista/Coletor** autenticado encerre sua sessão de forma segura, invalidando o token JWT e interrompendo o compartilhamento de localização em tempo real. O logout garante que o dispositivo compartilhado não permaneça com a sessão ativa após o uso.

### 1.2 Cenário de Negócio

> O motorista terminou sua rota de coleta, clica em "Sair" no menu. O sistema para de compartilhar sua localização, invalida a sessão e redireciona para a página inicial. O dispositivo fica seguro para o próximo motorista.

---

## 2. Descrição Geral

### 2.1 Perspectiva do Produto

O Logout opera em **três etapas**:

1. **Interrupção do rastreamento:** Para o `watchPosition` e fecha a conexão WebSocket ativa.
2. **Invalidação da sessão:** Chama `supabase.auth.signOut()` para revogar o JWT.
3. **Redirecionamento:** Navega o usuário para a página inicial (`/`).

### 2.2 Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| **RF-AUT2-01** | O sistema deve exibir um botão/link "Sair" visível no header da Área do Coletor. |
| **RF-AUT2-02** | Ao clicar em "Sair", o sistema deve interromper imediatamente o compartilhamento de localização (parar `watchPosition` e fechar WebSocket). |
| **RF-AUT2-03** | O sistema deve revogar o token JWT via `supabase.auth.signOut()`. |
| **RF-AUT2-04** | O sistema deve limpar todos os dados de sessão armazenados localmente (localStorage/sessionStorage). |
| **RF-AUT2-05** | Após logout, o sistema deve redirecionar o usuário para a página inicial (`/`). |
| **RF-AUT2-06** | Após logout, qualquer tentativa de acessar rotas protegidas deve redirecionar para a página inicial. |

---

## 3. Entradas e Saídas

### 3.1 Entradas (Inputs)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| — | Clique no botão "Sair" | ✅ | Ação do usuário para iniciar o logout. |

### 3.2 Saídas (Outputs)

| Cenário | Saída |
|---------|-------|
| **Sucesso** | Sessão encerrada. WebSocket fechado. Redirecionamento para `/`. |
| **Falha (rede)** | Limpeza local executada. Redirecionamento para `/` mesmo sem confirmação do servidor. |

---

## 4. Regras de Negócio e Restrições

- **RN-AUT2-01 (Limpeza Completa):** O logout deve limpar JWT, dados de sessão e parar todos os processos em background (geolocalização, WebSocket) independentemente do status da rede.
- **RN-AUT2-02 (Logout Gracioso):** Se a conexão WebSocket estiver ativa, o sistema deve enviar uma mensagem de desconexão ao servidor antes de fechar, para que o backend marque o caminhão como "offline".
- **RN-AUT2-03 (Sessão Expirada):** Tokens JWT expirados devem resultar em logout automático na próxima interação do usuário, sem necessidade de ação manual.

---

## 5. Casos de Uso

### UC-AUT-02: Logout do Motorista

| Campo | Descrição |
|-------|-----------| 
| **Ator primário** | Motorista/Coletor |
| **Pré-condições** | Usuário autenticado com sessão ativa. |
| **Fluxo principal** | 1. Motorista clica em "Sair" no header. <br> 2. Sistema para o compartilhamento de localização. <br> 3. Sistema fecha a conexão WebSocket. <br> 4. Sistema chama `supabase.auth.signOut()`. <br> 5. Sistema limpa dados locais. <br> 6. Redireciona para `/`. |
| **Fluxo alternativo** | Sessão expira automaticamente → sistema executa passos 2-6 automaticamente. |
| **Fluxo de exceção** | Falha de rede → sistema executa passos 2, 4-local, 5 e 6 (limpeza local sem confirmação do servidor). |
| **Pós-condições** | Sessão encerrada. Caminhão marcado como offline no backend. Dispositivo limpo. |

---

## 6. Critérios de Aceite

| ID | Critério | Formato Given-When-Then |
|:--:|---------|------------------------|
| CA-AUT2-01 | Logout manual | **Dado que** o motorista está autenticado na Área do Coletor, **quando** clica em "Sair", **então** a sessão é encerrada, o WebSocket é fechado e ele é redirecionado para `/`. |
| CA-AUT2-02 | Proteção de rotas | **Dado que** o motorista fez logout, **quando** tenta acessar `/coletor` diretamente via URL, **então** é redirecionado para `/` sem acesso à área protegida. |
| CA-AUT2-03 | Parada de rastreamento | **Dado que** o motorista está com localização ativa, **quando** faz logout, **então** o GPS para de ser capturado e o backend marca o caminhão como offline em menos de 5 segundos. |
| CA-AUT2-04 | Sessão expirada | **Dado que** o token JWT do motorista expirou, **quando** ele tenta qualquer interação, **então** é automaticamente deslogado e redirecionado para `/`. |
