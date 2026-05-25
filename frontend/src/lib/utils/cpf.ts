/**
 * Cadê o Lixeiro? v2.0 — Utilitários de CPF
 *
 * Validação de dígitos verificadores, formatação visual e
 * conversão para e-mail fictício (Supabase Auth).
 * Ref: AUT-1 SDD §4.1
 */

/** Valida dígitos verificadores do CPF */
export function validarCPF(cpf: string): boolean {
    const limpo = cpf.replace(/\D/g, '')
    if (limpo.length !== 11 || /^(\d)\1+$/.test(limpo)) return false

    for (let t = 9; t < 11; t++) {
        let d = 0
        for (let c = 0; c < t; c++) {
            d += parseInt(limpo[c]) * ((t + 1) - c)
        }
        d = ((10 * d) % 11) % 10
        if (parseInt(limpo[t]) !== d) return false
    }
    return true
}

/** Formata CPF limpo como e-mail fictício para Supabase Auth */
export function cpfToEmail(cpf: string): string {
    return `${cpf.replace(/\D/g, '')}@cadeolixeiro.internal`
}

/** Aplica máscara visual: 12345678909 → 123.456.789-09 */
export function mascaraCPF(valor: string): string {
    return valor
        .replace(/\D/g, '')
        .slice(0, 11)
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d{1,2})$/, '$1-$2')
}
