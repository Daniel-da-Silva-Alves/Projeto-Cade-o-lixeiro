/**
 * Cadê o Lixeiro? v2.0 — Auth Store (Svelte 5 Runes)
 *
 * Estado de autenticação reativo com login/logout e onAuthStateChange.
 * Ref: AUT-1 SDD §4.2 + AUT-2 SDD §4.1
 */

import { goto } from '$app/navigation'
import { supabase } from '$lib/supabase'
import { cpfToEmail, validarCPF } from '$lib/utils/cpf'

const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000'

/** Dados do motorista autenticado */
interface MotoristaProfile {
    nome: string
    ativo: boolean
    caminhao_id: string | null
}

/** Estado de autenticação */
let usuario = $state<MotoristaProfile | null>(null)
let carregando = $state(true)
let erro = $state<string | null>(null)

/** Retorna estado reativo (read-only) */
export function getAuth() {
    return {
        get usuario() { return usuario },
        get carregando() { return carregando },
        get erro() { return erro },
        get autenticado() { return usuario !== null && usuario.ativo },
    }
}

/**
 * Login via CPF + Senha
 * 1. Valida CPF → 2. signInWithPassword → 3. Valida perfil via FastAPI
 */
export async function login(cpf: string, senha: string): Promise<boolean> {
    erro = null

    // 1. Validar CPF
    const cpfLimpo = cpf.replace(/\D/g, '')
    if (!validarCPF(cpfLimpo)) {
        erro = 'CPF inválido.'
        return false
    }

    // 2. Autenticação via Supabase Auth
    const { data, error } = await supabase.auth.signInWithPassword({
        email: cpfToEmail(cpfLimpo),
        password: senha,
    })

    if (error) {
        erro = 'CPF ou senha incorretos.'
        return false
    }

    // 3. Validação de perfil via FastAPI
    try {
        const res = await fetch(`${API_URL}/api/auth/validar-perfil`, {
            headers: {
                'Authorization': `Bearer ${data.session.access_token}`,
            },
        })

        if (!res.ok) {
            await supabase.auth.signOut()
            erro = 'Perfil não encontrado. Contate o administrador.'
            return false
        }

        const perfil: MotoristaProfile = await res.json()

        if (!perfil.ativo) {
            await supabase.auth.signOut()
            erro = 'Acesso não autorizado. Contate o administrador.'
            return false
        }

        if (!perfil.caminhao_id) {
            await supabase.auth.signOut()
            erro = 'Nenhum veículo associado ao seu perfil.'
            return false
        }

        usuario = perfil
        localStorage.setItem('motorista', JSON.stringify(perfil))
        return true
    } catch {
        await supabase.auth.signOut()
        erro = 'Erro de conexão com o servidor.'
        return false
    }
}

/**
 * Logout do motorista
 * 1. Para rastreamento (GPS + WS) → 2. signOut → 3. Limpa dados → 4. Redireciona
 */
export async function logout() {
    // 1. Parar rastreamento (será integrado na FASE 5)
    // pararRastreamento()

    // 2. Revogar JWT no Supabase
    await supabase.auth.signOut()

    // 3. Limpar dados locais
    usuario = null
    localStorage.removeItem('motorista')
    sessionStorage.clear()

    // 4. Redirecionar
    goto('/')
}

/**
 * Inicializa o listener de auth state change.
 * Deve ser chamado uma vez no layout principal.
 */
export function inicializarAuth() {
    // Restaurar dados do localStorage
    const cached = localStorage.getItem('motorista')
    if (cached) {
        try {
            usuario = JSON.parse(cached)
        } catch {
            localStorage.removeItem('motorista')
        }
    }

    // Listener de mudanças de autenticação
    supabase.auth.onAuthStateChange(async (event, session) => {
        if (event === 'SIGNED_OUT' || !session) {
            usuario = null
            localStorage.removeItem('motorista')
        }
        carregando = false
    })

    // Verificar sessão existente
    supabase.auth.getSession().then(({ data: { session } }) => {
        if (!session) {
            usuario = null
            localStorage.removeItem('motorista')
        }
        carregando = false
    })
}
