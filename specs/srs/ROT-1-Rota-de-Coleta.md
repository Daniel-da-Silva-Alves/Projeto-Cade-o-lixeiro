# 📋 Especificação de Requisitos — ROT-1: Rota de Coleta (Motorista)

> **Funcionalidade:** ROT-1 — Visualização de Rota de Coleta
> **Módulo:** Rotas e Coleta
> **Versão:** 1.0
> **Referência:** IEEE 830 / ISO/IEC/IEEE 29148:2018

---

## 1. Introdução

### 1.1 Propósito

Exibir a **rota de coleta planejada** para o motorista autenticado, incluindo todos os pontos de parada com endereço, ordem e horário de passagem, renderizados no mapa com roteamento e em uma tabela interativa. O motorista visualiza sua posição atual em relação à rota e pode navegar entre os pontos.

### 1.2 Cenário de Negócio

> O motorista iniciou sua coleta. No mapa, vê a rota desenhada em verde com 12 pontos de parada numerados. Na tabela lateral, cada ponto mostra o endereço e horário previsto. Ao clicar no ponto 5, o mapa faz zoom e mostra o endereço detalhado. O ponto 3 já está marcado como "concluído" porque o caminhão já passou por lá.

---

## 2. Descrição Geral

### 2.1 Perspectiva do Produto

A rota de coleta é exibida dentro da **Área do Coletor** (`/coletor`):

1. **Mapa** com rota desenhada (Leaflet Routing Machine) e waypoints numerados.
2. **Tabela colapsável** com lista de pontos ordenados, endereço e horário.
3. **Interatividade**: clique na tabela faz zoom no ponto; clique no marcador mostra detalhes.
4. **Ícones diferenciados**: início (🟢), fim (🔴), pontos intermediários (📍).

### 2.2 Requisitos Funcionais

| ID | Requisito |
|----|-----------|
| **RF-ROT1-01** | O sistema deve carregar automaticamente a rota associada ao caminhão do motorista logado via `GET /api/rotas/{truck_id}/localizacoes`. |
| **RF-ROT1-02** | O sistema deve renderizar a rota completa no mapa com Leaflet Routing Machine, com linha verde conectando todos os waypoints. |
| **RF-ROT1-03** | O sistema deve exibir marcadores diferenciados: ícone de início (verde) para o primeiro ponto, ícone de fim (vermelho) para o último, e ícone padrão para intermediários. |
| **RF-ROT1-04** | O sistema deve exibir uma tabela colapsável com: ordem, endereço e horário de passagem de cada ponto da rota. |
| **RF-ROT1-05** | Ao clicar em uma linha da tabela, o mapa deve fazer zoom no ponto correspondente e abrir o popup com detalhes. |
| **RF-ROT1-06** | Ao clicar em um marcador no mapa, o sistema deve exibir popup com: "Ponto de coleta [N]", endereço e horário previsto. |
| **RF-ROT1-07** | O sistema deve destacar visualmente na tabela a linha do ponto clicado (estado ativo). |
| **RF-ROT1-08** | O sistema deve exibir mensagem "Nenhuma rota encontrada para seu veículo" se o caminhão não tiver rota cadastrada. |

---

## 3. Entradas e Saídas

### 3.1 Entradas (Inputs)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `truck_id` | String (do JWT) | ✅ | ID do caminhão associado ao motorista logado. Extraído automaticamente do token. |

### 3.2 Saídas (Outputs)

| Cenário | Saída |
|---------|-------|
| **Rota encontrada** | Mapa com rota desenhada + tabela com pontos ordenados. |
| **Sem rota** | Mensagem "Nenhuma rota encontrada para seu veículo. Contate o administrador." |
| **Erro na API** | Mensagem de erro + retry automático. |

---

## 4. Regras de Negócio e Restrições

- **RN-ROT-01 (Autenticação):** Apenas motoristas autenticados podem acessar rotas. A rota exibida é sempre a do caminhão associado ao motorista logado.
- **RN-ROT-02 (Ordenação):** Os pontos da rota são exibidos na ordem definida pelo campo `order` (crescente).
- **RN-ROT-03 (Horários):** O campo `passage_time` é exibido em formato HH:MM ao lado de cada ponto.
- **RN-ROT-04 (Rota Única):** Cada caminhão possui no máximo uma rota ativa por vez.

---

## 5. Casos de Uso

### UC-ROT-01: Visualizar Rota de Coleta

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Motorista/Coletor |
| **Pré-condições** | Motorista autenticado. Rota cadastrada para o caminhão. |
| **Fluxo principal** | 1. Motorista acessa `/coletor`. <br> 2. Sistema carrega rota do caminhão automaticamente. <br> 3. Mapa renderiza rota com waypoints. <br> 4. Tabela exibe pontos com endereço e horário. <br> 5. Motorista clica em ponto para zoom. |
| **Fluxo alternativo** | Sem rota → mensagem informativa. |
| **Fluxo de exceção** | API indisponível → retry automático. |
| **Pós-condições** | Rota exibida no mapa e tabela. |

---

## 6. Critérios de Aceite

| ID | Critério | Formato Given-When-Then |
|:--:|---------|------------------------|
| CA-ROT1-01 | Carregamento automático | **Dado que** o motorista está autenticado e seu caminhão tem rota cadastrada, **quando** acessa `/coletor`, **então** a rota é renderizada no mapa com todos os waypoints em menos de 3 segundos. |
| CA-ROT1-02 | Interatividade tabela-mapa | **Dado que** a rota possui 10 pontos, **quando** o motorista clica no ponto 5 na tabela, **então** o mapa faz zoom para o ponto 5 e abre popup com endereço e horário. |
| CA-ROT1-03 | Ícones diferenciados | **Dado que** a rota tem 8 pontos, **quando** renderizada no mapa, **então** o ponto 1 tem ícone verde (início), o ponto 8 tem ícone vermelho (fim), e os pontos 2-7 têm ícone padrão. |
| CA-ROT1-04 | Sem rota | **Dado que** o caminhão do motorista não tem rota cadastrada, **quando** acessa `/coletor`, **então** exibe mensagem "Nenhuma rota encontrada para seu veículo." |
