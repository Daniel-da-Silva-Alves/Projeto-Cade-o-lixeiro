# 📋 Especificação de Requisitos — ADM-1: Painel Administrativo

> **Funcionalidade:** ADM-1 — Painel Administrativo
> **Módulo:** Administração do Sistema
> **Versão:** 1.0
> **Referência:** IEEE 830 / ISO/IEC/IEEE 29148:2018

---

## 1. Introdução

### 1.1 Propósito

Fornecer uma interface administrativa completa para **gestão de todas as entidades do sistema**: caminhões, motoristas, rotas, locais de descarte, bairros e denúncias. O painel é dividido em duas camadas: **SQLAdmin** para CRUD rápido das entidades e **Dashboard Svelte** para relatórios visuais e métricas operacionais.

### 1.2 Cenário de Negócio

> O gestor da frota acessa o painel administrativo. Na dashboard, vê que 12 de 20 caminhões estão ativos, 3 denúncias novas foram registradas hoje, e o bairro "Centro" lidera o ranking. Clica em "Gerenciar Caminhões" para cadastrar um novo veículo, associar um motorista e definir sua rota de coleta.

---

## 2. Descrição Geral

### 2.1 Perspectiva do Produto

O Painel Administrativo possui duas camadas:

1. **SQLAdmin (CRUD):** Interface auto-gerada a partir dos models SQLAlchemy. Acessível via `/admin/`. Oferece CRUD completo para todas as entidades.
2. **Dashboard Svelte (Relatórios):** Interface customizada em Svelte com gráficos e métricas. Acessível via `/dashboard/` no frontend.

### 2.2 Requisitos Funcionais

#### SQLAdmin (CRUD)

| ID | Requisito |
|----|-----------|
| **RF-ADM1-01** | O sistema deve fornecer CRUD completo para a entidade **Caminhão** (truck_id, modelo, placa, bairro de operação). |
| **RF-ADM1-02** | O sistema deve fornecer CRUD completo para a entidade **Motorista** (nome, CPF, caminhão associado, status ativo/inativo). |
| **RF-ADM1-03** | O sistema deve fornecer CRUD para a entidade **Rota** com inline de **Pontos da Rota** (endereço, coordenadas, ordem, horário de passagem, dias da semana, tipo de coleta). |
| **RF-ADM1-04** | O sistema deve fornecer CRUD para a entidade **Local de Descarte** (nome, coordenadas, endereço, bairro, tipos de resíduo, horário de funcionamento). |
| **RF-ADM1-05** | O sistema deve fornecer CRUD para a entidade **Bairro** (nome, geometria PostGIS opcional). |
| **RF-ADM1-06** | O sistema deve fornecer gestão de **Denúncias**: visualizar, alterar status (pendente → em andamento → resolvida → descartada), e visualizar fotos anexadas. |
| **RF-ADM1-07** | Ao cadastrar motorista, o sistema deve criar automaticamente o usuário no Supabase Auth com e-mail fictício `{CPF}@cadeolixeiro.internal` e senha temporária. |
| **RF-ADM1-08** | O sistema deve exigir autenticação de administrador para acesso ao painel. |

#### Dashboard Svelte (Relatórios)

| ID | Requisito |
|----|-----------|
| **RF-ADM1-09** | O dashboard deve exibir **KPIs principais**: caminhões ativos/total, denúncias pendentes, rotas cadastradas, locais de descarte. |
| **RF-ADM1-10** | O dashboard deve exibir **mapa de calor** com localização das denúncias (agrupadas por bairro). |
| **RF-ADM1-11** | O dashboard deve exibir **gráfico** de denúncias por status (pendente, em andamento, resolvida, descartada) ao longo do tempo. |
| **RF-ADM1-12** | O dashboard deve exibir **ranking de bairros** com gráfico comparativo. |
| **RF-ADM1-13** | O dashboard deve exibir **rastreamento em tempo real** de todos os caminhões ativos no mapa. |

---

## 3. Entradas e Saídas

### 3.1 Entradas (Inputs)

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| Credenciais admin | Username + Senha | ✅ | Autenticação do administrador. |
| Dados de entidades | Formulários CRUD | ✅ | Dados das entidades para criação/edição. |

### 3.2 Saídas (Outputs)

| Cenário | Saída |
|---------|-------|
| **Login admin — sucesso** | Acesso ao SQLAdmin e Dashboard. |
| **Login admin — falha** | Mensagem de erro. |
| **CRUD — sucesso** | Toast de confirmação + lista atualizada. |
| **Dashboard** | KPIs, gráficos e mapa em tempo real. |

---

## 4. Regras de Negócio e Restrições

- **RN-ADM-01 (Acesso Restrito):** Apenas usuários com role `admin` no Supabase Auth podem acessar o painel.
- **RN-ADM-02 (Criação de Motorista):** Ao criar motorista no SQLAdmin, o sistema deve automaticamente criar o usuário correspondente no Supabase Auth. A senha temporária deve ser comunicada ao admin para repasse ao motorista.
- **RN-ADM-03 (Desativação de Motorista):** Desativar um motorista não exclui seus dados, apenas impede login.
- **RN-ADM-04 (Denúncias):** Admin não pode excluir denúncias, apenas alterar status. Todas as mudanças de status são registradas com timestamp para timeline.
- **RN-ADM-05 (Bairros):** A adição/edição de bairros atualiza automaticamente o dropdown de filtros em todas as interfaces públicas.

---

## 5. Casos de Uso

### UC-ADM-01: Cadastrar Caminhão e Motorista

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Administrador |
| **Pré-condições** | Admin autenticado no painel. |
| **Fluxo principal** | 1. Admin acessa SQLAdmin → Caminhões → Novo. <br> 2. Preenche: truck_id, modelo, placa, bairro. <br> 3. Salva caminhão. <br> 4. Acessa Motoristas → Novo. <br> 5. Preenche: nome, CPF, seleciona caminhão. <br> 6. Sistema cria usuário no Supabase Auth com senha temporária. <br> 7. Admin repassa credenciais ao motorista. |
| **Fluxo alternativo** | — |
| **Fluxo de exceção** | CPF duplicado → erro "CPF já cadastrado". |
| **Pós-condições** | Caminhão e motorista cadastrados. Motorista pode fazer login. |

### UC-ADM-02: Gerenciar Denúncia

| Campo | Descrição |
|-------|-----------|
| **Ator primário** | Administrador |
| **Pré-condições** | Denúncia registrada no sistema. |
| **Fluxo principal** | 1. Admin acessa SQLAdmin → Denúncias. <br> 2. Filtra por status `pendente`. <br> 3. Clica em uma denúncia para visualizar detalhes e fotos. <br> 4. Altera status para `em_andamento`. <br> 5. Após resolução, altera para `resolvida`. <br> 6. Sistema registra timestamps e atualiza ranking do bairro. |
| **Fluxo alternativo** | Denúncia falsa → altera status para `descartada`. |
| **Fluxo de exceção** | — |
| **Pós-condições** | Status atualizado. Timeline registrada. Ranking impactado se resolvida. |

---

## 6. Critérios de Aceite

| ID | Critério | Formato Given-When-Then |
|:--:|---------|------------------------|
| CA-ADM-01 | Acesso restrito | **Dado que** um usuário sem role `admin` tenta acessar `/admin/`, **quando** a requisição é processada, **então** é redirecionado para a página de login com mensagem "Acesso negado". |
| CA-ADM-02 | Cadastro de motorista | **Dado que** o admin cadastra motorista com CPF `123.456.789-09`, **quando** salva, **então** um usuário é criado no Supabase Auth com e-mail `12345678909@cadeolixeiro.internal` e senha temporária é exibida. |
| CA-ADM-03 | Gestão de denúncia | **Dado que** existe uma denúncia com status `pendente`, **quando** o admin altera para `resolvida`, **então** o status é atualizado, timestamp é registrado, e a pontuação do bairro no ranking aumenta. |
| CA-ADM-04 | KPIs do dashboard | **Dado que** existem 20 caminhões (12 ativos), 5 denúncias pendentes, **quando** o admin acessa `/dashboard/`, **então** os KPIs exibem "12/20 caminhões ativos" e "5 denúncias pendentes". |
| CA-ADM-05 | Mapa em tempo real | **Dado que** o admin está no dashboard, **quando** visualiza o mapa, **então** vê todos os caminhões ativos com posições atualizando em tempo real via WebSocket. |
