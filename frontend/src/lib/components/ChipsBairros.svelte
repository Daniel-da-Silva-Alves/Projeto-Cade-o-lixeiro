<script lang="ts">
  const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

  let {
    selecionados = $bindable<string[]>([]),
    onBuscar = () => {},
  }: {
    selecionados?: string[];
    onBuscar?: () => void;
  } = $props();

  let bairros = $state<{id: string; nome: string}[]>([]);
  let busca = $state('');

  async function carregarBairros() {
    try {
      const res = await fetch(`${API_URL}/api/bairros`);
      if (res.ok) {
        const data = await res.json();
        bairros = data.bairros || [];
      }
    } catch { /* silent */ }
  }

  $effect(() => { carregarBairros(); });

  function toggle(id: string) {
    if (selecionados.includes(id)) {
      selecionados = selecionados.filter(s => s !== id);
    } else {
      selecionados = [...selecionados, id];
    }
  }

  let filtrados = $derived(
    busca.trim()
      ? bairros.filter(b => b.nome.toLowerCase().includes(busca.toLowerCase()))
      : bairros
  );
</script>

<div>
  <input
    type="text"
    placeholder="Filtrar bairros..."
    bind:value={busca}
    class="mb-3 w-full rounded-lg border border-surface-200 bg-white px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200"
  />

  <div class="flex max-h-[200px] flex-wrap gap-1.5 overflow-y-auto">
    {#each filtrados as bairro}
      <button
        onclick={() => toggle(bairro.id)}
        class="rounded-full px-3 py-1 text-xs font-medium transition-all"
        class:bg-primary-600={selecionados.includes(bairro.id)}
        class:text-white={selecionados.includes(bairro.id)}
        class:bg-surface-100={!selecionados.includes(bairro.id)}
        class:text-surface-700={!selecionados.includes(bairro.id)}
        class:hover:bg-surface-200={!selecionados.includes(bairro.id)}
      >
        {bairro.nome}
      </button>
    {/each}
  </div>

  {#if selecionados.length > 0}
    <button
      onclick={onBuscar}
      class="mt-3 w-full rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-primary-700"
    >
      🔍 Buscar rotas ({selecionados.length} bairro{selecionados.length > 1 ? 's' : ''})
    </button>
  {/if}
</div>
