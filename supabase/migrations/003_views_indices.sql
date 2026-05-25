-- ============================================
-- Migration 003: Views Materializadas e Índices
-- Cadê o Lixeiro? v2.0
-- ============================================
-- Referências:
--   - GAM-1 SDD §3.1 (mv_ranking_mensal)
--   - DSC-1 SDD §3.3 (índice GiST bairros)
-- ============================================

-- 1. Materialized View: Ranking mensal de bairros
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ranking_mensal AS
SELECT
    b.id AS bairro_id,
    b.nome AS bairro,
    COALESCE(den.total_resolvidas, 0) AS denuncias_resolvidas,
    COALESCE(aval.total_descartes, 0) AS descartes_corretos,
    (COALESCE(den.total_resolvidas, 0) * 2
     + COALESCE(aval.total_descartes, 0) * 1) AS pontuacao,
    EXTRACT(MONTH FROM now()) AS mes,
    EXTRACT(YEAR FROM now()) AS ano
FROM public.bairros b
LEFT JOIN (
    SELECT bairro_id, COUNT(*) AS total_resolvidas
    FROM public.denuncias
    WHERE status = 'resolvida'
      AND EXTRACT(MONTH FROM updated_at) = EXTRACT(MONTH FROM now())
      AND EXTRACT(YEAR FROM updated_at) = EXTRACT(YEAR FROM now())
    GROUP BY bairro_id
) den ON den.bairro_id = b.id
LEFT JOIN (
    SELECT ld.bairro_id, COUNT(*) AS total_descartes
    FROM public.avaliacoes_descarte ad
    JOIN public.locais_descarte ld ON ld.id = ad.local_id
    WHERE ad.estrelas >= 4
      AND EXTRACT(MONTH FROM ad.created_at) = EXTRACT(MONTH FROM now())
      AND EXTRACT(YEAR FROM ad.created_at) = EXTRACT(YEAR FROM now())
    GROUP BY ld.bairro_id
) aval ON aval.bairro_id = b.id
ORDER BY pontuacao DESC;

-- Índice único para REFRESH CONCURRENTLY
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_ranking_bairro ON mv_ranking_mensal (bairro_id);
