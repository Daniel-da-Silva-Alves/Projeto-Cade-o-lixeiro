<script lang="ts">
  import { login, getAuth } from '$lib/stores/auth.svelte';
  import { mascaraCPF } from '$lib/utils/cpf';
  import { goto } from '$app/navigation';

  const auth = getAuth();

  let cpf = $state('');
  let senha = $state('');
  let enviando = $state(false);
  let mostrarSenha = $state(false);

  function handleCpfInput(e: Event) {
    const input = e.target as HTMLInputElement;
    cpf = mascaraCPF(input.value);
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();
    enviando = true;

    const sucesso = await login(cpf, senha);

    if (sucesso) {
      goto('/coletor');
    }

    enviando = false;
  }
</script>

<div class="mx-auto w-full max-w-md">
  <div class="rounded-2xl border border-surface-200 bg-white p-8 shadow-lg">
    <!-- Header -->
    <div class="mb-8 text-center">
      <div class="mb-3 text-4xl">🚛</div>
      <h1 class="text-2xl font-bold text-surface-900">Área do Motorista</h1>
      <p class="mt-1 text-sm text-surface-500">Faça login com seu CPF e senha</p>
    </div>

    <!-- Form -->
    <form onsubmit={handleSubmit} class="space-y-5">
      <!-- CPF -->
      <div>
        <label for="cpf" class="mb-1.5 block text-sm font-medium text-surface-700">
          CPF
        </label>
        <input
          id="cpf"
          type="text"
          inputmode="numeric"
          placeholder="000.000.000-00"
          value={cpf}
          oninput={handleCpfInput}
          maxlength="14"
          required
          autocomplete="username"
          class="w-full rounded-lg border border-surface-300 px-4 py-2.5 text-surface-900 placeholder:text-surface-400 transition-all focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
        />
      </div>

      <!-- Senha -->
      <div>
        <label for="senha" class="mb-1.5 block text-sm font-medium text-surface-700">
          Senha
        </label>
        <div class="relative">
          <input
            id="senha"
            type={mostrarSenha ? 'text' : 'password'}
            placeholder="••••••••"
            bind:value={senha}
            required
            autocomplete="current-password"
            class="w-full rounded-lg border border-surface-300 px-4 py-2.5 pr-10 text-surface-900 placeholder:text-surface-400 transition-all focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          />
          <button
            type="button"
            onclick={() => (mostrarSenha = !mostrarSenha)}
            class="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-surface-600"
            aria-label={mostrarSenha ? 'Ocultar senha' : 'Mostrar senha'}
          >
            {#if mostrarSenha}
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
              </svg>
            {:else}
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            {/if}
          </button>
        </div>
      </div>

      <!-- Erro -->
      {#if auth.erro}
        <div class="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          ⚠️ {auth.erro}
        </div>
      {/if}

      <!-- Submit -->
      <button
        type="submit"
        disabled={enviando || !cpf || !senha}
        class="w-full rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-primary-700 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50"
      >
        {#if enviando}
          <span class="inline-flex items-center gap-2">
            <svg class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            Entrando...
          </span>
        {:else}
          Entrar
        {/if}
      </button>
    </form>

    <!-- Rodapé -->
    <p class="mt-6 text-center text-xs text-surface-400">
      Acesso exclusivo para motoristas cadastrados.
      <br />
      Em caso de problemas, contate o administrador.
    </p>
  </div>
</div>
