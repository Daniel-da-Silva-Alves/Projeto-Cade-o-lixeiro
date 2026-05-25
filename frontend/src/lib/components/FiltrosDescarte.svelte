<script lang="ts">
  const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

  let {
    bairroSelecionado = $bindable(''),
    tipoSelecionado = $bindable(''),
    busca = $bindable(''),
    onFiltrar = () => {},
  }: {
    bairroSelecionado?: string;
    tipoSelecionado?: string;
    busca?: string;
    onFiltrar?: () => void;
  } = $props();

  let bairros = $state<{id: string; nome: string}[]>([]);

  const tipos = [
    { value: '', label: 'Todos os tipos' },
    { value: 'reciclavel', label: '♻️ Reciclável' },
    { value: 'organico', label: '🌱 Orgânico' },
    { value: 'eletronico', label: '💻 Eletrônico' },
    { value: 'oleo', label: '🛢️ Óleo' },
    { value: 'pilhas', label: '🔋 Pilhas/Baterias' },
    { value: 'vidro', label: '🪟 Vidro' },
    { value: 'papel', label: '📄 Papel' },
    { value: 'metal', label: '🔩 Metal' },
    { value: 'plastico', label: '🧴 Plástico' },
    { value: 'verde', label: '🌿 Resíduo Verde' },
  ];

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
</script>

<div class="flex flex-col gap-3 sm:flex-row sm:items-end">
  <!-- Bairro -->
  <div class="flex-1">
    <label for="filtro-bairro" class="mb-1 block text-xs font-semibold uppercase tracking-wider text-surface-500">Bairro</label>
    <select
      id="filtro-bairro"
      bind:value={bairroSelecionado}
      onchange={onFiltrar}
      class="w-full rounded-lg border border-surface-200 bg-white px-3 py-2 text-sm text-surface-800 shadow-sm transition-colors focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200"
    >
      <option value="">Todos os bairros</option>
      {#each bairros as b}
        <option value={b.id}>{b.nome}</option>
      {/each}
    </select>
  </div>

  <!-- Tipo -->
  <div class="flex-1">
    <label for="filtro-tipo" class="mb-1 block text-xs font-semibold uppercase tracking-wider text-surface-500">Tipo de Resíduo</label>
    <select
      id="filtro-tipo"
      bind:value={tipoSelecionado}
      onchange={onFiltrar}
      class="w-full rounded-lg border border-surface-200 bg-white px-3 py-2 text-sm text-surface-800 shadow-sm transition-colors focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200"
    >
      {#each tipos as t}
        <option value={t.value}>{t.label}</option>
      {/each}
    </select>
  </div>

  <!-- Busca -->
  <div class="flex-1">
    <label for="filtro-busca" class="mb-1 block text-xs font-semibold uppercase tracking-wider text-surface-500">Buscar</label>
    <input
      id="filtro-busca"
      type="text"
      placeholder="Nome ou endereço..."
      bind:value={busca}
      oninput={onFiltrar}
      class="w-full rounded-lg border border-surface-200 bg-white px-3 py-2 text-sm text-surface-800 shadow-sm transition-colors focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200"
    />
  </div>
</div>
