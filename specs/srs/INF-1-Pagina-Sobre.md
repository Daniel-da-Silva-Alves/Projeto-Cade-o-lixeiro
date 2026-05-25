# 📋 Especificação de Requisitos — INF-1: Página Sobre

> **Funcionalidade:** INF-1 — Página Sobre
> **Módulo:** Informacional
> **Versão:** 1.0
> **Referência:** IEEE 830 / ISO/IEC/IEEE 29148:2018

---

## 1. Introdução

### 1.1 Propósito

Fornecer uma página institucional estática que apresenta o projeto **"Cadê o Lixeiro?"**, sua missão, equipe, tecnologias utilizadas e canais de contato. A página substitui o link externo para o Notion que existia na versão legada, trazendo o conteúdo para dentro da aplicação.

### 1.2 Cenário de Negócio

> O cidadão ou parceiro institucional acessa o menu de navegação, clica em "Sobre" e visualiza uma página completa com a história do projeto, seus objetivos ambientais, a equipe responsável e formas de contribuir ou entrar em contato.

A página reforça a **credibilidade institucional** do projeto e serve como ponto de entrada para novos colaboradores open source.

---

## 2. Descrição Geral

### 2.1 Perspectiva do Produto

A página Sobre é uma rota estática dentro do SvelteKit (`/sobre`) que não requer autenticação nem chamadas à API. O conteúdo é definido diretamente no componente Svelte.

### 2.2 Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| **RF-INF1-01** | O sistema deve exibir uma página acessível via rota `/sobre` no menu de navegação principal. |
| **RF-INF1-02** | A página deve apresentar seções: Missão do Projeto, Funcionalidades Principais, Equipe, Tecnologias Utilizadas e Contato. |
| **RF-INF1-03** | A página deve ser responsiva, adaptando-se a dispositivos móveis e desktop. |
| **RF-INF1-04** | A página deve conter links de navegação para retorno à página inicial e demais seções do sistema. |
| **RF-INF1-05** | A página deve exibir o link do repositório GitHub para contribuições open source. |

---

## 3. Entradas e Saídas

### 3.1 Entradas (Inputs)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|---------  |
| — | — | — | Nenhuma entrada do usuário. Página estática. |

### 3.2 Saídas (Outputs)

| Cenário | Saída |
|---------|-------|
| **Acesso à página** | Renderização do conteúdo institucional com layout responsivo e animações sutis. |

---

## 4. Regras de Negócio e Restrições

- **RN-INF-01 (Acesso Público):** A página deve ser acessível sem autenticação, para qualquer visitante.
- **RN-INF-02 (SEO):** A página deve incluir meta tags adequadas (title, description, og:image) para compartilhamento em redes sociais.
- **RN-INF-03 (Performance):** Nenhuma chamada à API deve ser feita. Todo conteúdo é estático e renderizado no build.

---

## 5. Casos de Uso

### UC-INF-01: Visualizar Página Sobre

| Campo | Descrição |
|-------|-----------| 
| **Ator primário** | Cidadão / Visitante |
| **Pré-condições** | Nenhuma. |
| **Fluxo principal** | 1. Usuário acessa o menu de navegação. <br> 2. Clica em "Sobre". <br> 3. Sistema renderiza a página `/sobre` com conteúdo institucional. |
| **Fluxo alternativo** | Acesso direto via URL `/sobre`. |
| **Fluxo de exceção** | Nenhum. |
| **Pós-condições** | Página renderizada com sucesso. |

---

## 6. Critérios de Aceite

| ID | Critério | Formato Given-When-Then |
|:--:|---------|------------------------|
| CA-INF-01 | Acesso via menu | **Dado que** o usuário está em qualquer página do sistema, **quando** clica em "Sobre" no menu de navegação, **então** é redirecionado para `/sobre` e visualiza o conteúdo institucional completo. |
| CA-INF-02 | Responsividade | **Dado que** o usuário acessa `/sobre` em um dispositivo mobile (< 768px), **quando** a página carrega, **então** o layout se adapta sem scroll horizontal e com tipografia legível. |
| CA-INF-03 | Link GitHub | **Dado que** o usuário visualiza a página Sobre, **quando** clica no link do repositório GitHub, **então** é redirecionado para `https://github.com/Daniel-da-Silva-Alves/Projeto-Cade-o-lixeiro` em nova aba. |
