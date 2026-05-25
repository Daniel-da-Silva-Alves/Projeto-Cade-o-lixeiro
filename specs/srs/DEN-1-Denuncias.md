# 📋 Especificação de Requisitos — DEN-1: Denúncias Anônimas

> **Funcionalidade:** DEN-1 — Sistema de Denúncias Ambientais Anônimas
> **Módulo:** Fiscalização e Participação Cidadã
> **Versão:** 1.0
> **Referência:** IEEE 830 / ISO/IEC/IEEE 29148:2018

---

## 1. Introdução

### 1.1 Propósito

Permitir que o cidadão registre **denúncias ambientais anônimas** sobre áreas contaminadas, incêndios criminosos ou descartes ilegais, com evidências fotográficas e localização geográfica. As denúncias são rastreáveis por status (pendente → em andamento → resolvida) e alimentam o **ranking de sustentabilidade** dos bairros.

### 1.2 Cenário de Negócio

> O cidadão encontra um terreno baldio com lixo acumulado no bairro. Abre o app, clica em "Denunciar", seleciona "Área Contaminada", tira uma foto, e o GPS marca automaticamente a localização. A denúncia é registrada anonimamente. O cidadão pode acompanhar o status pela ID da denúncia. Quando resolvida, o bairro ganha pontos no ranking.

---

## 2. Descrição Geral

### 2.1 Perspectiva do Produto

O sistema de denúncias opera em duas interfaces:

1. **Interface do cidadão** (`/denunciar`): Formulário de denúncia + acompanhamento por ID.
2. **Interface administrativa** (SQLAdmin/Dashboard): Gestão de denúncias, atualização de status.

### 2.2 Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| **RF-DEN1-01** | O sistema deve exibir um formulário de denúncia com: tipo (dropdown), descrição (textarea), foto (upload), e localização (mapa com GPS + ajuste manual). |
| **RF-DEN1-02** | Os tipos de denúncia disponíveis devem ser: `area_contaminada` (Área Contaminada), `incendio_criminoso` (Incêndio Criminoso), `descarte_ilegal` (Descarte Ilegal). |
| **RF-DEN1-03** | O sistema deve capturar automaticamente a localização do cidadão via GPS ao abrir o formulário, posicionando um marcador no mapa. |
| **RF-DEN1-04** | O cidadão deve poder **ajustar manualmente** a localização da denúncia arrastando o marcador no mapa. |
| **RF-DEN1-05** | O sistema deve permitir upload de **1 a 3 fotos** como evidência, armazenadas no Supabase Storage. |
| **RF-DEN1-06** | Cada foto deve ter tamanho máximo de **5MB** e formatos aceitos: JPG, PNG, WEBP. |
| **RF-DEN1-07** | Ao submeter a denúncia, o sistema deve gerar um **ID de acompanhamento** único (ex: `DEN-2026-00142`) e exibi-lo ao cidadão. |
| **RF-DEN1-08** | O sistema deve permitir consultar o **status de uma denúncia** informando o ID de acompanhamento, sem necessidade de login. |
| **RF-DEN1-09** | Os status possíveis de uma denúncia são: `pendente`, `em_andamento`, `resolvida`, `descartada`. |
| **RF-DEN1-10** | Quando uma denúncia é marcada como `resolvida`, o sistema deve incrementar a pontuação do bairro correspondente no ranking (GAM-1). |
| **RF-DEN1-11** | O sistema deve geocodificar automaticamente as coordenadas da denúncia para identificar o **bairro** (via PostGIS ou Nominatim com cache). |
| **RF-DEN1-12** | Denúncias são **anônimas** — nenhum dado pessoal é coletado ou armazenado. |

---

## 3. Entradas e Saídas

### 3.1 Entradas (Inputs)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `tipo` | Enum (dropdown) | ✅ | Tipo da denúncia: `area_contaminada`, `incendio_criminoso`, `descarte_ilegal`. |
| `descricao` | String (textarea, max 1000 chars) | ✅ | Descrição detalhada do problema. |
| `fotos` | Array de arquivos (1-3 imagens) | ✅ | Evidências fotográficas. Max 5MB cada, JPG/PNG/WEBP. |
| `latitude` | Float | ✅ | Latitude do local (GPS automático ou ajuste manual). |
| `longitude` | Float | ✅ | Longitude do local (GPS automático ou ajuste manual). |
| `id_acompanhamento` | String | ✅* | ID para consulta de status. *Obrigatório apenas na consulta. |

### 3.2 Saídas (Outputs)

| Cenário | Saída |
|---------|-------|
| **Denúncia registrada** | Toast "Denúncia registrada com sucesso!" + ID de acompanhamento exibido com opção de copiar. |
| **Consulta de status** | Card com: tipo, data, status atual, bairro, e timeline de atualizações. |
| **ID inválido** | Mensagem "Denúncia não encontrada. Verifique o código informado." |
| **Erro no upload** | Mensagem "Erro ao enviar foto. Verifique o tamanho e formato." |

---

## 4. Regras de Negócio e Restrições

- **RN-DEN-01 (Anonimato):** Nenhum dado pessoal (nome, e-mail, IP) é associado à denúncia no banco de dados. O IP é usado apenas para rate limiting em memória.
- **RN-DEN-02 (Rate Limiting):** Máximo de 5 denúncias por IP a cada 24 horas para evitar spam.
- **RN-DEN-03 (Armazenamento de Fotos):** Fotos são armazenadas no Supabase Storage no bucket `denuncias/{DEN-ID}/`. URLs são referenciadas no registro da denúncia no PostgreSQL.
- **RN-DEN-04 (Identificação de Bairro):** O bairro da denúncia é determinado automaticamente pelas coordenadas, usando query espacial PostGIS (tabela `bairros` com geometria) ou fallback para Nominatim.
- **RN-DEN-05 (Impacto no Ranking):** Apenas denúncias com status `resolvida` contam para o ranking do bairro (GAM-1). Denúncias `descartadas` não contam.
- **RN-DEN-06 (ID de Acompanhamento):** Formato: `DEN-{ANO}-{SEQUENCIAL_5_DIGITOS}`. Exemplo: `DEN-2026-00142`.

---

## 5. Casos de Uso

### UC-DEN-01: Registrar Denúncia Anônima

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Cidadão |
| **Pré-condições** | Nenhuma (anônimo, sem login). |
| **Fluxo principal** | 1. Cidadão acessa `/denunciar`. <br> 2. GPS detecta localização e posiciona marcador. <br> 3. Cidadão seleciona tipo, digita descrição, envia fotos. <br> 4. Opcionalmente ajusta localização no mapa. <br> 5. Clica em "Enviar denúncia". <br> 6. Sistema registra, geocodifica bairro, armazena fotos. <br> 7. Exibe ID de acompanhamento. |
| **Fluxo alternativo** | GPS negado → cidadão posiciona marcador manualmente no mapa. |
| **Fluxo de exceção** | Rate limit → "Limite de denúncias atingido. Tente novamente amanhã." <br> Upload falha → "Erro ao enviar foto." |
| **Pós-condições** | Denúncia registrada com status `pendente`. ID de acompanhamento disponível. |

### UC-DEN-02: Consultar Status de Denúncia

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Cidadão |
| **Pré-condições** | Posse do ID de acompanhamento. |
| **Fluxo principal** | 1. Cidadão acessa `/denunciar` e localiza campo "Acompanhar denúncia". <br> 2. Digita o ID (ex: `DEN-2026-00142`). <br> 3. Sistema busca e exibe: tipo, data, status, bairro, timeline. |
| **Fluxo alternativo** | — |
| **Fluxo de exceção** | ID inválido → "Denúncia não encontrada." |
| **Pós-condições** | Status exibido. |

---

## 6. Critérios de Aceite

| ID | Critério | Formato Given-When-Then |
|:--:|---------|------------------------|
| CA-DEN-01 | Registro com GPS | **Dado que** o cidadão permitiu GPS e está em Flores, **quando** abre `/denunciar`, **então** o marcador posiciona automaticamente na localização atual e o bairro "Flores" é detectado. |
| CA-DEN-02 | Ajuste manual | **Dado que** o GPS posicionou o marcador incorretamente, **quando** o cidadão arrasta o marcador 500m ao norte, **então** a nova coordenada é usada e o bairro é recalculado. |
| CA-DEN-03 | Upload de fotos | **Dado que** o cidadão anexou 2 fotos (1.5MB e 3MB, JPG), **quando** submete a denúncia, **então** as fotos são armazenadas no Supabase Storage e referenciadas no registro. |
| CA-DEN-04 | ID de acompanhamento | **Dado que** a denúncia foi registrada com sucesso, **quando** o sistema confirma, **então** exibe um ID no formato `DEN-2026-XXXXX` com botão de copiar. |
| CA-DEN-05 | Consulta de status | **Dado que** o cidadão possui o ID `DEN-2026-00142`, **quando** consulta o status, **então** vê tipo "Área Contaminada", status "Em andamento", e timeline com datas de cada mudança de status. |
| CA-DEN-06 | Impacto no ranking | **Dado que** a denúncia `DEN-2026-00142` no bairro "Centro" é marcada como `resolvida` pelo admin, **quando** o ranking é recalculado, **então** a pontuação do "Centro" aumenta em 2 pontos. |
| CA-DEN-07 | Rate limiting | **Dado que** o cidadão já enviou 5 denúncias nas últimas 24h, **quando** tenta a 6ª, **então** o sistema rejeita com mensagem de limite atingido. |
