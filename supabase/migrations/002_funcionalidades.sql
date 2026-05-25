-- ============================================
-- Migration 002: Tabelas de Funcionalidades
-- Cadê o Lixeiro? v2.0
-- ============================================
-- Referências:
--   - DSC-1 SDD §3.1-3.2 (locais_descarte, avaliacoes)
--   - RAT-1 SDD §3.1 (localizacoes_caminhao)
--   - RAT-2 SDD §3.1 (cache_geocodificacao)
--   - DEN-1 SDD §3.1-3.2 (denuncias, timeline_status)
--   - NOT-1 SDD §3.1-3.2 (subscriptions_push, log_notificacoes)
-- ============================================

-- 1. Locais de descarte consciente
CREATE TABLE IF NOT EXISTS public.locais_descarte (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome            TEXT NOT NULL,
    endereco        TEXT NOT NULL,
    latitude        DOUBLE PRECISION NOT NULL,
    longitude       DOUBLE PRECISION NOT NULL,
    bairro_id       UUID NOT NULL REFERENCES public.bairros(id),
    tipos_residuo   TEXT[] NOT NULL,                     -- ['organic','electronics',...]
    horarios        JSONB,                               -- {"seg":"08:00-17:00",...}
    telefone        TEXT,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_locais_bairro ON public.locais_descarte (bairro_id);
CREATE INDEX IF NOT EXISTS idx_locais_tipos ON public.locais_descarte USING GIN (tipos_residuo);

-- 2. Avaliações anônimas de locais de descarte
CREATE TABLE IF NOT EXISTS public.avaliacoes_descarte (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    local_id        UUID NOT NULL REFERENCES public.locais_descarte(id) ON DELETE CASCADE,
    estrelas        SMALLINT NOT NULL CHECK (estrelas BETWEEN 1 AND 5),
    comentario      TEXT,
    ip_hash         TEXT NOT NULL,                       -- SHA256 do IP
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_avaliacoes_local ON public.avaliacoes_descarte (local_id);
CREATE INDEX IF NOT EXISTS idx_avaliacoes_ip ON public.avaliacoes_descarte (ip_hash, created_at);

-- 3. Histórico de localizações dos caminhões
CREATE TABLE IF NOT EXISTS public.localizacoes_caminhao (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    caminhao_id UUID NOT NULL REFERENCES public.caminhoes(id),
    latitude    DOUBLE PRECISION NOT NULL,
    longitude   DOUBLE PRECISION NOT NULL,
    endereco    TEXT,                                    -- Geocodificado assincronamente
    cep         TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_loc_caminhao ON public.localizacoes_caminhao (caminhao_id, created_at DESC);

-- 4. Cache de geocodificação (Nominatim, raio 50m)
CREATE TABLE IF NOT EXISTS public.cache_geocodificacao (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    latitude    DOUBLE PRECISION NOT NULL,
    longitude   DOUBLE PRECISION NOT NULL,
    geom        GEOMETRY(POINT, 4326) NOT NULL,
    endereco    TEXT NOT NULL,
    bairro_id   UUID REFERENCES public.bairros(id),
    cep         TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cache_geom ON public.cache_geocodificacao USING GIST (geom);

-- 5. Denúncias ambientais anônimas
CREATE SEQUENCE IF NOT EXISTS seq_denuncia_id START 1;

CREATE TABLE IF NOT EXISTS public.denuncias (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_acompanhamento   TEXT NOT NULL UNIQUE,             -- DEN-2026-00142
    tipo                TEXT NOT NULL CHECK (tipo IN (
        'area_contaminada', 'incendio_criminoso', 'descarte_ilegal'
    )),
    descricao           TEXT NOT NULL,
    latitude            DOUBLE PRECISION NOT NULL,
    longitude           DOUBLE PRECISION NOT NULL,
    bairro_id           UUID REFERENCES public.bairros(id),
    status              TEXT NOT NULL DEFAULT 'pendente' CHECK (status IN (
        'pendente', 'em_andamento', 'resolvida', 'descartada'
    )),
    fotos_urls          TEXT[] NOT NULL DEFAULT '{}',     -- URLs do Supabase Storage
    ip_hash             TEXT NOT NULL,                    -- SHA256 para rate limiting
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_denuncias_status ON public.denuncias (status);
CREATE INDEX IF NOT EXISTS idx_denuncias_bairro ON public.denuncias (bairro_id);
CREATE INDEX IF NOT EXISTS idx_denuncias_acompanhamento ON public.denuncias (id_acompanhamento);

-- 6. Timeline de mudanças de status das denúncias
CREATE TABLE IF NOT EXISTS public.timeline_status (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    denuncia_id     UUID NOT NULL REFERENCES public.denuncias(id) ON DELETE CASCADE,
    status_anterior TEXT,
    status_novo     TEXT NOT NULL,
    observacao      TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_timeline_denuncia ON public.timeline_status (denuncia_id, created_at);

-- 7. Subscriptions de push notification
CREATE TABLE IF NOT EXISTS public.subscriptions_push (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bairro_id   UUID NOT NULL REFERENCES public.bairros(id),
    endpoint    TEXT NOT NULL UNIQUE,
    p256dh      TEXT NOT NULL,
    auth_key    TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_subs_bairro ON public.subscriptions_push (bairro_id);

-- 8. Log anti-spam de notificações
CREATE TABLE IF NOT EXISTS public.log_notificacoes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bairro_id   UUID NOT NULL,
    caminhao_id UUID NOT NULL,
    enviado_em  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_log_antispam ON public.log_notificacoes (bairro_id, caminhao_id, enviado_em);
