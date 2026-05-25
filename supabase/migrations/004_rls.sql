-- ============================================
-- Migration 004: Row Level Security (RLS)
-- Cadê o Lixeiro? v2.0
-- ============================================
-- Políticas:
--   anon: SELECT em tabelas públicas
--   authenticated: SELECT + INSERT em tabelas de interação
--   service_role: ALL (bypass RLS por padrão)
-- ============================================

-- ==========================================
-- TABELAS PÚBLICAS (leitura para todos)
-- ==========================================

-- Bairros
ALTER TABLE public.bairros ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Bairros: leitura pública" ON public.bairros
    FOR SELECT USING (true);

-- Caminhões
ALTER TABLE public.caminhoes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Caminhoes: leitura pública" ON public.caminhoes
    FOR SELECT USING (true);

-- Rotas
ALTER TABLE public.rotas ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Rotas: leitura pública" ON public.rotas
    FOR SELECT USING (true);

-- Pontos de rota
ALTER TABLE public.pontos_rota ENABLE ROW LEVEL SECURITY;
CREATE POLICY "PontosRota: leitura pública" ON public.pontos_rota
    FOR SELECT USING (true);

-- Locais de descarte
ALTER TABLE public.locais_descarte ENABLE ROW LEVEL SECURITY;
CREATE POLICY "LocaisDescarte: leitura pública" ON public.locais_descarte
    FOR SELECT USING (true);

-- Ranking (materialized view não suporta RLS, acessível via query direta)

-- ==========================================
-- TABELAS DE INTERAÇÃO (anon pode ler e inserir)
-- ==========================================

-- Avaliações de descarte
ALTER TABLE public.avaliacoes_descarte ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Avaliacoes: leitura pública" ON public.avaliacoes_descarte
    FOR SELECT USING (true);
CREATE POLICY "Avaliacoes: inserção anônima" ON public.avaliacoes_descarte
    FOR INSERT WITH CHECK (true);

-- Denúncias
ALTER TABLE public.denuncias ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Denuncias: leitura pública" ON public.denuncias
    FOR SELECT USING (true);
CREATE POLICY "Denuncias: inserção anônima" ON public.denuncias
    FOR INSERT WITH CHECK (true);

-- Timeline de status (somente leitura pública)
ALTER TABLE public.timeline_status ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Timeline: leitura pública" ON public.timeline_status
    FOR SELECT USING (true);

-- Subscriptions push
ALTER TABLE public.subscriptions_push ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Push: inserção anônima" ON public.subscriptions_push
    FOR INSERT WITH CHECK (true);
CREATE POLICY "Push: leitura própria" ON public.subscriptions_push
    FOR SELECT USING (true);

-- ==========================================
-- TABELAS PROTEGIDAS (somente service_role via backend)
-- ==========================================

-- Motoristas (gerenciado pelo backend/admin)
ALTER TABLE public.motoristas ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Motoristas: leitura autenticada" ON public.motoristas
    FOR SELECT TO authenticated USING (true);

-- Localizações (escritas pelo backend, leitura interna)
ALTER TABLE public.localizacoes_caminhao ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Localizacoes: leitura pública" ON public.localizacoes_caminhao
    FOR SELECT USING (true);

-- Cache geocodificação (somente backend)
ALTER TABLE public.cache_geocodificacao ENABLE ROW LEVEL SECURITY;

-- Log notificações (somente backend)
ALTER TABLE public.log_notificacoes ENABLE ROW LEVEL SECURITY;
