<script lang="ts">
  import TabelaRanking from '$lib/components/TabelaRanking.svelte';

  const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

  let periodo = $state<'mensal' | 'acumulado'>('mensal');
  let ranking = $state<any[]>([]);
  let carregando = $state(true);
  let erro = $state<string | null>(null);

  async function carregarRanking() {
    carregando = true;
    erro = null;
    try {
      const res = await fetch(`${API_URL}/api/ranking?periodo=${periodo}`);
      if (!res.ok) throw new Error('Erro ao carregar ranking');
      const data = await res.json();
      ranking = data.ranking;
    } catch (e) {
      erro = 'Erro ao carregar ranking. Tente novamente.';
      ranking = [];
    } finally {
      carregando = false;
    }
  }

  $effect(() => {
    carregarRanking();
  });

  function trocarPeriodo(p: 'mensal' | 'acumulado') {
    periodo = p;
  }
</script>

<svelte:head>
  <title>Ranking de Bairros — Cadê o Lixeiro?</title>
  <meta name="description" content="Ranking de sustentabilidade dos bairros de Manaus. Veja quais bairros têm mais denúncias resolvidas e descartes corretos." />
</svelte:head>

<div class="flex flex-col">
  <!-- Header -->
  <section class="bg-gradient-to-br from-amber-500 via-yellow-500 to-orange-500 px-4 py-12 text-white sm:px-6 lg:px-8">
    <div class="mx-auto max-w-4xl text-center">
      <span class="mb-3 inline-block text-5xl">🏆</span>
      <h1 class="text-3xl font-extrabold tracking-tight sm:text-4xl">
        Ranking de Bairros
      </h1>
      <p class="mx-auto mt-3 max-w-xl text-lg text-white/90">
        Os bairros mais sustentáveis de Manaus. A pontuação é calculada por denúncias resolvidas (×2) e descartes corretos (×1).
      </p>
    </div>
  </section>

  <!-- Content -->
  <section class="px-4 py-8 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-4xl">
      <!-- Tabs período -->
      <div class="mb-6 flex items-center justify-center gap-2">
        <button
          onclick={() => trocarPeriodo('mensal')}
          class="rounded-lg px-4 py-2 text-sm font-semibold transition-all"
          class:bg-primary-600={periodo === 'mensal'}
          class:text-white={periodo === 'mensal'}
          class:shadow-sm={periodo === 'mensal'}
          class:bg-surface-100={periodo !== 'mensal'}
          class:text-surface-700={periodo !== 'mensal'}
          class:hover:bg-surface-200={periodo !== 'mensal'}
        >
          📅 Mensal
        </button>
        <button
          onclick={() => trocarPeriodo('acumulado')}
          class="rounded-lg px-4 py-2 text-sm font-semibold transition-all"
          class:bg-primary-600={periodo === 'acumulado'}
          class:text-white={periodo === 'acumulado'}
          class:shadow-sm={periodo === 'acumulado'}
          class:bg-surface-100={periodo !== 'acumulado'}
          class:text-surface-700={periodo !== 'acumulado'}
          class:hover:bg-surface-200={periodo !== 'acumulado'}
        >
          📊 Acumulado
        </button>
      </div>

      <!-- Loading -->
      {#if carregando}
        <div class="flex items-center justify-center py-12">
          <svg class="h-8 w-8 animate-spin text-primary-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          <span class="ml-3 text-surface-500">Carregando ranking...</span>
        </div>
      {:else if erro}
        <div class="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
          <span class="text-3xl">⚠️</span>
          <p class="mt-2 text-sm text-red-700">{erro}</p>
          <button
            onclick={carregarRanking}
            class="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition-all hover:bg-red-700"
          >
            Tentar novamente
          </button>
        </div>
      {:else}
        <TabelaRanking {ranking} {periodo} />
      {/if}

      <!-- Info -->
      <div class="mt-8 rounded-xl border border-surface-200 bg-surface-50 p-4">
        <h3 class="text-sm font-semibold text-surface-700">ℹ️ Como funciona a pontuação?</h3>
        <ul class="mt-2 space-y-1 text-sm text-surface-600">
          <li>📢 Cada <strong>denúncia resolvida</strong> no bairro vale <strong>2 pontos</strong></li>
          <li>♻️ Cada <strong>descarte avaliado positivamente</strong> (≥ 4 estrelas) vale <strong>1 ponto</strong></li>
          <li>🔄 O ranking mensal é atualizado automaticamente a cada hora</li>
        </ul>
      </div>
    </div>
  </section>
</div>
