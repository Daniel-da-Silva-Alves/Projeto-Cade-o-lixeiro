<script lang="ts">
  import FiltrosDescarte from '$lib/components/FiltrosDescarte.svelte';
  import CardLocalDescarte from '$lib/components/CardLocalDescarte.svelte';

  const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

  interface LocalDescarte {
    id: string; nome: string; endereco: string;
    latitude: number; longitude: number; bairro: string;
    tipos_residuo: string[]; horarios: Record<string, string>;
    telefone: string | null; avaliacao_media: number; total_avaliacoes: number;
  }

  let bairroSelecionado = $state('');
  let tipoSelecionado = $state('');
  let busca = $state('');
  let locais = $state<LocalDescarte[]>([]);
  let carregando = $state(true);
  let localSelecionado = $state<LocalDescarte | null>(null);
  let mapaComponente: any = $state(null);
  let L: any = null;
  let marcadores: any[] = [];

  async function carregarLocais() {
    carregando = true;
    try {
      const params = new URLSearchParams();
      if (bairroSelecionado) params.set('bairro_id', bairroSelecionado);
      if (tipoSelecionado) params.set('tipo', tipoSelecionado);
      if (busca.trim()) params.set('busca', busca.trim());

      const res = await fetch(`${API_URL}/api/descarte?${params}`);
      if (res.ok) {
        const data = await res.json();
        locais = data.locais;
        atualizarMarcadores();
      }
    } catch { /* silent */ }
    carregando = false;
  }

  function atualizarMarcadores() {
    if (!mapaComponente || !L) return;

    // Limpar marcadores antigos
    marcadores.forEach(m => m.remove());
    marcadores = [];

    locais.forEach(local => {
      const marker = L.marker([local.latitude, local.longitude], {
        icon: L.divIcon({
          className: 'descarte-marker',
          html: `<div class="descarte-pin">♻️</div>`,
          iconSize: [30, 30],
          iconAnchor: [15, 15],
        }),
      })
        .addTo(mapaComponente)
        .bindPopup(`<strong>${local.nome}</strong><br>${local.endereco}`);

      marker.on('click', () => { localSelecionado = local; });
      marcadores.push(marker);
    });

    // fitBounds
    if (locais.length > 0) {
      const bounds = L.latLngBounds(locais.map(l => [l.latitude, l.longitude]));
      mapaComponente.fitBounds(bounds, { padding: [40, 40] });
    }
  }

  async function onMapReady(map: any) {
    mapaComponente = map;
    L = await import('leaflet');
    await carregarLocais();
  }

  $effect(() => {
    // Re-fetch when filters change (tracked by reading the state values)
    bairroSelecionado; tipoSelecionado; busca;
  });
</script>

<svelte:head>
  <title>Locais de Descarte — Cadê o Lixeiro?</title>
  <meta name="description" content="Encontre ecopontos e locais de descarte consciente em Manaus. Filtre por bairro, tipo de resíduo e busque por nome." />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</svelte:head>

<div class="flex flex-col">
  <!-- Header -->
  <section class="bg-gradient-to-br from-emerald-600 to-green-700 px-4 py-10 text-white sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl text-center">
      <span class="mb-2 inline-block text-4xl">♻️</span>
      <h1 class="text-3xl font-extrabold tracking-tight sm:text-4xl">Locais de Descarte</h1>
      <p class="mx-auto mt-2 max-w-xl text-base text-emerald-100">
        Encontre ecopontos, cooperativas e pontos de descarte consciente em Manaus.
      </p>
    </div>
  </section>

  <!-- Content -->
  <section class="px-4 py-6 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <!-- Filtros -->
      <div class="mb-6">
        <FiltrosDescarte
          bind:bairroSelecionado
          bind:tipoSelecionado
          bind:busca
          onFiltrar={carregarLocais}
        />
      </div>

      <!-- Layout: Mapa + Lista/Card -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Mapa -->
        <div class="lg:col-span-2">
          {#await import('$lib/components/Mapa/MapaBase.svelte') then MapaModule}
            <MapaModule.default
              height="500px"
              showGPS={true}
              onMapReady={onMapReady}
            />
          {/await}
        </div>

        <!-- Sidebar -->
        <div class="flex flex-col gap-4">
          {#if localSelecionado}
            <CardLocalDescarte
              local={localSelecionado}
              onFechar={() => { localSelecionado = null; }}
            />
          {/if}

          <!-- Lista resumida -->
          <div class="rounded-xl border border-surface-200 bg-white p-4 shadow-sm">
            <h3 class="mb-3 text-sm font-semibold uppercase tracking-wider text-surface-500">
              {carregando ? 'Carregando...' : `${locais.length} locais encontrados`}
            </h3>
            {#if !carregando && locais.length === 0}
              <p class="text-sm text-surface-500">Nenhum local encontrado com os filtros selecionados.</p>
            {:else}
              <div class="max-h-[400px] space-y-2 overflow-y-auto">
                {#each locais as local}
                  <button
                    onclick={() => {
                      localSelecionado = local;
                      if (mapaComponente) mapaComponente.setView([local.latitude, local.longitude], 16);
                    }}
                    class="w-full rounded-lg border border-surface-100 p-3 text-left transition-all hover:border-primary-300 hover:bg-primary-50"
                    class:border-primary-400={localSelecionado?.id === local.id}
                    class:bg-primary-50={localSelecionado?.id === local.id}
                  >
                    <p class="text-sm font-semibold text-surface-900">{local.nome}</p>
                    <p class="text-xs text-surface-500">{local.endereco}</p>
                    <div class="mt-1 flex items-center gap-1">
                      <span class="text-xs text-amber-500">{'★'.repeat(Math.round(local.avaliacao_media))}</span>
                      <span class="text-xs text-surface-400">{local.avaliacao_media}</span>
                    </div>
                  </button>
                {/each}
              </div>
            {/if}
          </div>
        </div>
      </div>
    </div>
  </section>
</div>

<style>
  :global(.descarte-pin) {
    font-size: 22px;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
  }
</style>
