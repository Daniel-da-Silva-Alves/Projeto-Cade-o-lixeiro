-- ============================================
-- Seed 002: Dados de Teste (Motorista + Caminhão)
-- Cadê o Lixeiro? v2.0
-- ============================================
-- ATENÇÃO: Este seed cria dados de teste.
-- NÃO usar em produção.
--
-- Credenciais de teste:
--   CPF: 123.456.789-09
--   Senha: teste123
-- ============================================

-- 1. Usuário de teste no Supabase Auth
-- Nota: Executar via Supabase Dashboard ou MCP, pois requer acesso ao schema auth.
-- INSERT INTO auth.users (...)

-- 2. Caminhão de teste
INSERT INTO public.caminhoes (truck_id, modelo, placa)
VALUES ('CAM-001', 'VW Constellation 17.280', 'OAM-0001')
ON CONFLICT (truck_id) DO NOTHING;

-- 3. Motorista de teste (requer auth_id e caminhao_id)
-- Nota: Os IDs abaixo são gerados dinamicamente. Ajustar conforme ambiente.
-- INSERT INTO public.motoristas (auth_id, nome, cpf, caminhao_id, status)
-- VALUES ('<auth_user_id>', 'Carlos Teste', '12345678909', '<caminhao_id>', 'ativo');
