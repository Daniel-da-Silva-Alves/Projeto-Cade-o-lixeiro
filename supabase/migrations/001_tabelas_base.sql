-- ============================================
-- Migration 001: Tabelas Base
-- Cadê o Lixeiro? v2.0
-- ============================================
-- Dependência: extensão PostGIS já habilitada
-- Referências:
--   - DSC-1 SDD §3.3 (bairros)
--   - RAT-1 SDD §3.2 (caminhoes)
--   - AUT-1 SDD §3.1 (motoristas)
--   - HOR-1 SDD §3.1-3.2 (rotas, pontos_rota)
-- ============================================

-- 1. Bairros de Manaus
CREATE TABLE IF NOT EXISTS public.bairros (
    id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome    TEXT NOT NULL UNIQUE,
    geom    GEOMETRY(POLYGON, 4326)  -- PostGIS (opcional, para resolução espacial)
);

CREATE INDEX IF NOT EXISTS idx_bairros_geom ON public.bairros USING GIST (geom);

-- 2. Caminhões de coleta
CREATE TABLE IF NOT EXISTS public.caminhoes (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    truck_id            TEXT NOT NULL UNIQUE,           -- Identificador legível: CAM-001
    modelo              TEXT,
    placa               TEXT UNIQUE,
    status              TEXT NOT NULL DEFAULT 'offline'
                        CHECK (status IN ('online', 'offline')),
    ultima_posicao_lat  DOUBLE PRECISION,
    ultima_posicao_lng  DOUBLE PRECISION,
    ultimo_endereco     TEXT,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);

-- 3. Motoristas (vinculados a auth.users via Supabase Auth)
CREATE TABLE IF NOT EXISTS public.motoristas (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    nome            TEXT NOT NULL,
    cpf             VARCHAR(11) NOT NULL UNIQUE,
    caminhao_id     UUID REFERENCES public.caminhoes(id),
    status          TEXT NOT NULL DEFAULT 'ativo'
                    CHECK (status IN ('ativo', 'inativo')),
    data_nascimento DATE,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_motoristas_cpf ON public.motoristas (cpf);
CREATE UNIQUE INDEX IF NOT EXISTS idx_motoristas_auth_id ON public.motoristas (auth_id);

-- 4. Rotas de coleta
CREATE TABLE IF NOT EXISTS public.rotas (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    caminhao_id     UUID NOT NULL REFERENCES public.caminhoes(id),
    rota_id         TEXT NOT NULL UNIQUE,               -- Identificador legível: ROT-001
    bairro_id       UUID NOT NULL REFERENCES public.bairros(id),
    tipo_coleta     TEXT NOT NULL DEFAULT 'geral'
                    CHECK (tipo_coleta IN ('organico','reciclavel','perigoso','verde','geral')),
    dias_semana     TEXT[] NOT NULL DEFAULT '{}',        -- ['seg','qua','sex']
    endereco_inicio TEXT,
    endereco_fim    TEXT,
    ativa           BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- 5. Pontos de uma rota (com horário de passagem)
CREATE TABLE IF NOT EXISTS public.pontos_rota (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rota_id          UUID NOT NULL REFERENCES public.rotas(id) ON DELETE CASCADE,
    endereco         TEXT NOT NULL,
    latitude         DOUBLE PRECISION NOT NULL,
    longitude        DOUBLE PRECISION NOT NULL,
    cep              TEXT,
    ordem            SMALLINT NOT NULL,
    horario_passagem TIME NOT NULL,
    created_at       TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pontos_rota ON public.pontos_rota (rota_id, ordem);
