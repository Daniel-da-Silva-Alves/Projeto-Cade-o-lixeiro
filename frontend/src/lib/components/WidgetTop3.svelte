<script lang="ts">
  const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

  interface Top3Item {
    posicao: number;
    medalha: string;
    bairro: string;
    pontuacao: number;
    denuncias_resolvidas: number;
    descartes_corretos: number;
  }

  let top3 = $state<Top3Item[]>([]);
  let carregando = $state(true);
  let erro = $state(false);

  async function carregarTop3() {
    try {
      const res = await fetch(`${API_URL}/api/ranking/top3`);
      if (res.ok) {
        const data = await res.json();
        top3 = data.top3;
      }
    } catch {
      erro = true;
    } finally {
      carregando = false;
    }
  }

  $effect(() => {
    carregarTop3();
  });

  const cores = [
    'from-amber-400 to-yellow-500',   // 🥇
    'from-slate-300 to-slate-400',     // 🥈
    'from-orange-400 to-amber-600',    // 🥉
  ];
</script>

<div class="rounded-xl border border-surface-200 bg-white p-6 shadow-sm">
  <div class="mb-4 flex items-center justify-between">
    <h3 class="text-lg font-bold text-surface-900">
      🏆 Top Bairros
    </h3>
    <a
      href="/ranking"
      class="text-sm font-medium text-primary-600 transition-colors hover:text-primary-700"
    >
      Ver ranking completo →
    </a>
  </div>

  {#if carregando}
    <div class="flex items-center justify-center py-8">
      <svg class="h-6 w-6 animate-spin text-primary-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
    </div>
  {:else if top3.length === 0}
    <div class="py-6 text-center">
      <span class="text-3xl">🌱</span>
      <p class="mt-2 text-sm text-surface-500">
        O ranking será populado conforme a comunidade participar.
      </p>
    </div>
  {:else}
    <div class="space-y-3">
      {#each top3 as item, i}
        <div class="flex items-center gap-4 rounded-lg bg-surface-50 p-3 transition-all hover:bg-surface-100">
          <div class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br {cores[i]} text-white shadow-sm">
            <span class="text-lg font-bold">{item.posicao}</span>
          </div>
          <div class="flex-1">
            <p class="font-semibold text-surface-900">{item.bairro}</p>
            <p class="text-xs text-surface-500">
              {item.denuncias_resolvidas} denúncias · {item.descartes_corretos} descartes
            </p>
          </div>
          <div class="text-right">
            <span class="text-lg font-bold text-primary-700">{item.pontuacao}</span>
            <span class="text-xs text-surface-400">pts</span>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
