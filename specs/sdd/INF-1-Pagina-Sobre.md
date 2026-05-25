# 📐 SDD — INF-1: Página Sobre

> **Funcionalidade:** INF-1 — Página Sobre
> **Documento:** Software Design Description
> **Norma de Referência:** IEEE 1016-2009
> **Versão:** 1.0
> **Data:** 24/05/2026
> **Requisito de Origem:** [INF-1 — SRS](../srs/INF-1-Pagina-Sobre.md)

---

## 1. Visão Geral e Stack

### 1.1 Contexto e Motivação

A página Sobre substitui o link externo (Notion) da versão legada, trazendo o conteúdo institucional para dentro da aplicação SvelteKit. É uma página 100% estática, sem chamadas à API, renderizada no build.

### 1.2 Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|---|---|---|
| **Framework** | SvelteKit (adapter-static) | SPA com file-based routing |
| **Linguagem** | TypeScript + Svelte 5 (runes) | Tipagem + reatividade |
| **Estilização** | Tailwind CSS v4 | CSS-first, utilitário |
| **Ícones** | Lucide Icons (via lucide-svelte) | Leve, MIT license |
| **Hosting** | Appwrite (static hosting) | Deploy automático |

---

## 2. Visão de Decomposição

### 2.1 Arquivos Criados

```
frontend/
└── src/
    └── routes/
        └── sobre/
            └── +page.svelte          ← Página Sobre
```

### 2.2 Componentes e Responsabilidades

| Componente | Responsabilidade |
|---|---|
| `+page.svelte` | Renderiza conteúdo estático: missão, funcionalidades, equipe, stack, contato |
| `+page.ts` | Metadados SEO (title, description) |

---

## 3. Modelagem de Dados

Nenhuma entidade de banco de dados. Conteúdo estático definido diretamente no componente Svelte.

---

## 4. Visão de Interface (Contratos)

### 4.1 Rotas

| Método | Rota | Componente | Descrição |
|---|---|---|---|
| GET | `/sobre` | `+page.svelte` | Renderiza página estática |

### 4.2 Layout

A página utiliza o layout principal (`+layout.svelte`) que inclui:
- Header com navegação (logo + links)
- Footer com créditos

### 4.3 Seções da Página

```svelte
<!-- Estrutura de +page.svelte -->
<svelte:head>
    <title>Sobre — Cadê o Lixeiro?</title>
    <meta name="description" content="Conheça o projeto Cadê o Lixeiro..."/>
</svelte:head>

<section id="missao">       <!-- Missão do projeto -->
<section id="funcionalidades"> <!-- Grid de funcionalidades -->
<section id="equipe">       <!-- Cards da equipe -->
<section id="stack">         <!-- Badges de tecnologias -->
<section id="contato">       <!-- Links GitHub, redes sociais -->
```

---

## 5. Visão de Dependências

| Dependência | Tipo | Uso |
|---|---|---|
| `lucide-svelte` | Frontend | Ícones das seções |
| Layout principal | Interno | Header + Footer compartilhados |

---

## 6. Lógica de Processamento

Nenhuma lógica de processamento. Página 100% estática.

---

## 7. Mapeamento SRS → SDD

| Requisito SRS | Componente SDD | Status |
|---|---|---|
| **RF-INF1-01** — Rota `/sobre` no menu | `+page.svelte` + layout com nav link | ✅ |
| **RF-INF1-02** — Seções: Missão, Funcionalidades, Equipe, Stack, Contato | 5 sections no componente | ✅ |
| **RF-INF1-03** — Responsividade | Tailwind responsive utilities (sm/md/lg breakpoints) | ✅ |
| **RF-INF1-04** — Links de navegação | Layout header com menu | ✅ |
| **RF-INF1-05** — Link GitHub | Seção contato com link externo `target="_blank"` | ✅ |

---

## 8. Riscos e Considerações

| Risco | Probabilidade | Impacto | Mitigação |
|---|:---:|:---:|---|
| Conteúdo desatualizado | Baixa | Baixo | Conteúdo versionado no Git, fácil de atualizar |

---

## 9. Decisões Arquiteturais Registradas

| # | Decisão | Alternativa Descartada | Justificativa |
|:-:|---------|----------------------|---------------|
| 1 | Conteúdo hardcoded no Svelte | CMS headless (Strapi, Contentful) | Projeto pequeno, sem necessidade de CMS. Conteúdo muda raramente. |
| 2 | Sem chamada à API | Buscar conteúdo do README do GitHub | Simplicidade. Evita dependência externa para página estática. |
