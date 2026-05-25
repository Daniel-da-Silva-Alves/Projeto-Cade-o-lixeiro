# 📋 Especificação de Requisitos — AUT-1: Login do Motorista

> **Funcionalidade:** AUT-1 — Login do Motorista/Coletor
> **Módulo:** Autenticação e Gestão de Usuários
> **Versão:** 1.0
> **Referência:** IEEE 830 / ISO/IEC/IEEE 29148:2018

---

## 1. Introdução

### 1.1 Propósito

Controlar o acesso do perfil **Motorista/Coletor** ao sistema. O motorista se identifica pelo seu **CPF** e uma **senha pessoal**. A autenticação é gerenciada pelo Supabase Auth, usando o CPF formatado como e-mail fictício (`{CPF}@cadeolixeiro.internal`) para manter compatibilidade com o fluxo padrão de autenticação, sem expor o artifício técnico ao usuário.

### 1.2 Cenário de Negócio

> O motorista chega na garagem, pega o dispositivo do caminhão, digita seu CPF e senha. Em segundos está na Área do Coletor, pronto para iniciar o compartilhamento de localização e visualizar sua rota de coleta do dia.

A autenticação prioriza **velocidade e simplicidade** — CPF é um identificador que todo motorista conhece de cor.

---

## 2. Descrição Geral

### 2.1 Perspectiva do Produto

O Login do Motorista opera em **quatro etapas transparentes**:

1. **Exibição do formulário:** Tela/modal de login com campos `CPF` e `Senha`, sem menção a e-mail.
2. **Formatação silenciosa:** A camada de serviço formata `{CPF_limpo}@cadeolixeiro.internal` antes de qualquer chamada de rede.
3. **Autenticação via Supabase Auth:** O payload formatado é enviado ao endpoint `signInWithPassword`.
4. **Avaliação pós-autenticação:** O sistema verifica o perfil do usuário no banco. Se o motorista está ativo e associado a um caminhão, libera acesso à Área do Coletor.

### 2.2 Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| **RF-AUT1-01** | O sistema deve exibir um formulário de login com os campos `CPF` (texto com máscara `000.000.000-00`) e `Senha` (campo mascarado), sem mencionar e-mail. |
| **RF-AUT1-02** | O sistema deve, na camada de serviço, remover pontuação do CPF e transformá-lo no formato `{CPF}@cadeolixeiro.internal` antes de enviar a requisição de autenticação. |
| **RF-AUT1-03** | O sistema deve autenticar o usuário via `signInWithPassword` do Supabase Auth usando o e-mail fictício formatado e a senha informada. |
| **RF-AUT1-04** | Após autenticação bem-sucedida, o sistema deve verificar se o motorista está com status `ativo` e possui caminhão associado. |
| **RF-AUT1-05** | Caso a autenticação seja bem-sucedida e o motorista esteja ativo, o sistema deve redirecionar para a Área do Coletor (`/coletor`). |
| **RF-AUT1-06** | O sistema deve bloquear a autenticação e exibir mensagem de erro genérica quando: credenciais inválidas, usuário inativo, ou motorista sem caminhão associado. |
| **RF-AUT1-07** | O sistema deve aplicar máscara de CPF no campo de entrada (formatação visual automática: `000.000.000-00`). |
| **RF-AUT1-08** | O sistema deve validar o CPF no frontend antes de enviar (algoritmo de verificação dos dígitos). |

---

## 3. Entradas e Saídas

### 3.1 Entradas (Inputs)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `cpf` | String com máscara (14 chars) | ✅ | CPF do motorista no formato `000.000.000-00`. Validação de dígitos verificadores. |
| `senha` | String mascarada | ✅ | Senha pessoal do motorista. |

### 3.2 Saídas (Outputs)

| Cenário | Saída |
|---------|-------|
| **Sucesso — motorista ativo com caminhão** | JWT expedido + redirecionamento para Área do Coletor (`/coletor`). |
| **Falha — credencial inválida** | Mensagem de erro genérica: "CPF ou senha incorretos." Nenhuma informação sensível exposta. |
| **Falha — motorista inativo** | Mensagem de erro genérica: "Acesso não autorizado. Contate o administrador." |
| **Falha — motorista sem caminhão** | Mensagem de erro: "Nenhum veículo associado ao seu perfil. Contate o administrador." |
| **Falha — CPF inválido** | Mensagem no campo: "CPF inválido. Verifique os números digitados." |

---

## 4. Regras de Negócio e Restrições

- **RN-AUT1-01 (Mapeamento Interno):** O campo `CPF` jamais é enviado diretamente ao Supabase Auth. A formatação `{CPF}@cadeolixeiro.internal` ocorre exclusivamente na camada de serviço, invisível ao motorista.
- **RN-AUT1-02 (Validação de CPF):** O frontend deve validar os dígitos verificadores do CPF antes de submeter o formulário, rejeitando CPFs inválidos como `000.000.000-00` ou `111.111.111-11`.
- **RN-AUT1-03 (Bloqueio por Expiração):** Tokens JWT têm durabilidade de 8 horas (jornada de trabalho típica). Sessões expiradas forçam novo login.
- **RN-AUT1-04 (Senha Segura):** Senhas são armazenadas com hash pelo Supabase Auth (bcrypt). Nunca em texto plano.
- **RN-AUT1-05 (Rate Limiting):** Máximo de 5 tentativas de login por CPF a cada 15 minutos. Após exceder, bloqueio temporário de 15 minutos.

---

## 5. Casos de Uso

### UC-AUT-01: Autenticar como Motorista

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Motorista/Coletor |
| **Pré-condições** | Motorista cadastrado com status `ativo` e caminhão associado. |
| **Fluxo principal** | 1. Acesso à página/modal de Login. <br> 2. Digitação do CPF (com máscara automática) e Senha. <br> 3. Clique em "Entrar". <br> 4. Validação do CPF no frontend. <br> 5. Formatação silenciosa: `{CPF}@cadeolixeiro.internal`. <br> 6. Autenticação via `signInWithPassword` no Supabase Auth. <br> 7. Verificação de status ativo e caminhão associado. <br> 8. Redirecionamento para a Área do Coletor (`/coletor`). |
| **Fluxo alternativo** | CPF inválido → erro no campo antes de submeter. |
| **Fluxo de exceção** | Credencial inválida → mensagem genérica + limpa campo senha. <br> Motorista inativo → mensagem de acesso negado. <br> Rate limit excedido → mensagem de bloqueio temporário. |
| **Pós-condições** | JWT de sessão expedido e armazenado. Acesso à Área do Coletor permitido. |

---

## 6. Critérios de Aceite

| ID | Critério | Formato Given-When-Then |
|:--:|---------|------------------------|
| CA-AUT1-01 | Formatação Interna | **Dado que** o campo CPF é digitado `123.456.789-09`, **quando** clica em "Entrar", **então** a requisição ao Supabase Auth viaja com o e-mail `12345678909@cadeolixeiro.internal`, sem que o valor original seja visível ao usuário. |
| CA-AUT1-02 | CPF inválido | **Dado que** o motorista digita `111.111.111-11`, **quando** tenta submeter o formulário, **então** o sistema exibe erro "CPF inválido" sem enviar requisição ao servidor. |
| CA-AUT1-03 | Motorista inativo | **Dado que** o motorista com CPF `123.456.789-09` tem status `inativo`, **quando** informa credenciais corretas, **então** o acesso é negado com mensagem genérica. |
| CA-AUT1-04 | Login bem-sucedido | **Dado que** o motorista informa CPF e senha corretos e está ativo com caminhão associado, **quando** a autenticação é concluída, **então** é redirecionado para `/coletor`. |
| CA-AUT1-05 | Rate limiting | **Dado que** o motorista errou a senha 5 vezes nos últimos 15 minutos, **quando** tenta o 6º login, **então** o sistema bloqueia e exibe "Muitas tentativas. Tente novamente em 15 minutos." |
| CA-AUT1-06 | Máscara de CPF | **Dado que** o motorista digita `12345678909` no campo CPF, **quando** digita os números, **então** o campo formata automaticamente para `123.456.789-09`. |
