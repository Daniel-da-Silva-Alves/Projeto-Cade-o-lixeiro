<script lang="ts">
  import ChipsBairros from '$lib/components/ChipsBairros.svelte';
  import TabelaRotas from '$lib/components/TabelaRotas.svelte';
  import { subscribePush, unsubscribePush, verificarSubscription } from '$lib/services/push';

  const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

  let bairrosSelecionados = $state<string[]>([]);
  let rotas = $state<any[]>([]);
  let pontos = $state<any[]>([]);
  let rotaSelecionada = $state<string | null>(null);
  let carregando = $state(false);
  let mapaComponente: any = $state(null);
  let L: any = null;
  let marcadoresRota: any[] = [];
  let polyline: any = null;
  let pushStatus = $state<Record<string, { subscribed: boolean; id?: string }>>({});
  let pushLoading = $state<Record<string, boolean>>({});

  async function toggleNotificacao(bairroId: string) {
    pushLoading[bairroId] = true;
    const status = pushStatus[bairroId];

    if (status?.subscribed && status.id) {
      const ok = await unsubscribePush(status.id);
      if (ok) {
        pushStatus[bairroId] = { subscribed: false };
      }
    } else {
      const result = await subscribePush(bairroId);
      if (result) {
        pushStatus[bairroId] = { subscribed: true, id: result.id };
      }
    }
    pushLoading[bairroId] = false;
    pushStatus = { ...pushStatus };
  }

  async function buscarRotas() {
    if (bairrosSelecionados.length === 0) return;
    carregando = true;
    try {
      const res = await fetch(`${API_URL}/api/rotas/por-bairro`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bairro_ids: bairrosSelecionados }),
      });
      if (res.ok) {
        const data = await res.json();
        rotas = data.rotas;
      }
    } catch { /* silent */ }
    carregando = false;
  }

  async function selecionarRota(rotaId: string) {
    rotaSelecionada = rotaId;
    try {
      const res = await fetch(`${API_URL}/api/rotas/${rotaId}/pontos`);
      if (res.ok) {
        const data = await res.json();
        pontos = data.pontos;
        desenharRota();
      }
    } catch { /* silent */ }
  }

  function desenharRota() {
    if (!mapaComponente || !L) return;

    // Limpar
    marcadoresRota.forEach(m => m.remove());
    marcadoresRota = [];
    if (polyline) { polyline.remove(); polyline = null; }

    if (pontos.length === 0) return;

    const coords = pontos.map(p => [p.latitude, p.longitude]);

    // Polyline
    polyline = L.polyline(coords, {
      color: '#059669',
      weight: 4,
      opacity: 0.8,
      dashArray: '10, 6',
    }).addTo(mapaComponente);

    // Marcadores com horário
    pontos.forEach((ponto, i) => {
      const isFirst = i === 0;
      const isLast = i === pontos.length - 1;

      const marker = L.marker([ponto.latitude, ponto.longitude], {
        icon: L.divIcon({
          className: 'ponto-rota-marker',
          html: `<div class="ponto-rota ${isFirst ? 'inicio' : isLast ? 'fim' : ''}">${ponto.ordem}</div>`,
          iconSize: [28, 28],
          iconAnchor: [14, 14],
        }),
      }).addTo(mapaComponente)
        .bindPopup(`
          <strong>${ponto.endereco}</strong><br>
          🕐 ${ponto.horario_passagem || 'N/D'}<br>
          📍 Ponto ${ponto.ordem}
        `);

      marcadoresRota.push(marker);
    });

    // fitBounds
    mapaComponente.fitBounds(L.latLngBounds(coords), { padding: [40, 40] });
  }

  async function onMapReady(map: any) {
    mapaComponente = map;
    L = await import('leaflet');
  }
</script>

<svelte:head>
  <title>Horários de Passagem — Cadê o Lixeiro?</title>
  <meta name="description" content="Consulte os horários e dias de passagem do caminhão de coleta no seu bairro em Manaus." />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</svelte:head>

<div class="flex flex-col">
  <!-- Header -->
  <section class="bg-gradient-to-br from-blue-600 to-indigo-700 px-4 py-10 text-white sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl text-center">
      <span class="mb-2 inline-block text-4xl">🕐</span>
      <h1 class="text-3xl font-extrabold tracking-tight sm:text-4xl">Horários de Passagem</h1>
      <p class="mx-auto mt-2 max-w-xl text-base text-blue-100">
        Selecione seus bairros e veja as rotas de coleta com horários de cada ponto.
      </p>
    </div>
  </section>

  <!-- Content -->
  <section class="px-4 py-6 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <!-- Seleção de bairros -->
      <div class="mb-6 rounded-xl border border-surface-200 bg-white p-4 shadow-sm">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-surface-500">Selecione os bairros</h2>
        <ChipsBairros bind:selecionados={bairrosSelecionados} onBuscar={buscarRotas} />

        {#if bairrosSelecionados.length > 0}
          <div class="mt-3 flex flex-wrap gap-2">
            {#each bairrosSelecionados as bid}
              <button
                onclick={() => toggleNotificacao(bid)}
                disabled={pushLoading[bid]}
                class="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold transition-all"
                class:bg-amber-100={!pushStatus[bid]?.subscribed}
                class:text-amber-700={!pushStatus[bid]?.subscribed}
                class:bg-emerald-100={pushStatus[bid]?.subscribed}
                class:text-emerald-700={pushStatus[bid]?.subscribed}
              >
                {pushStatus[bid]?.subscribed ? '🔔 Notificando' : '🔕 Ativar alerta'}
              </button>
            {/each}
          </div>
        {/if}
      </div>

      {#if carregando}
        <div class="flex items-center justify-center py-8">
          <svg class="h-6 w-6 animate-spin text-primary-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          <span class="ml-3 text-surface-500">Buscando rotas...</span>
        </div>
      {:else if rotas.length > 0}
        <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <!-- Tabela de rotas -->
          <div>
            <TabelaRotas {rotas} bind:rotaSelecionada onSelecionar={selecionarRota} />

            {#if pontos.length > 0}
              <div class="mt-4 rounded-xl border border-surface-200 bg-white p-4 shadow-sm">
                <h3 class="mb-2 text-sm font-semibold uppercase tracking-wider text-surface-500">
                  Pontos da Rota ({pontos.length})
                </h3>
                <div class="space-y-1">
                  {#each pontos as ponto}
                    <div class="flex items-center gap-3 rounded-lg bg-surface-50 px-3 py-2 text-sm">
                      <span class="flex h-6 w-6 items-center justify-center rounded-full bg-primary-600 text-xs font-bold text-white">{ponto.ordem}</span>
                      <span class="flex-1 text-surface-800">{ponto.endereco}</span>
                      <span class="font-medium text-primary-700">🕐 {ponto.horario_passagem || 'N/D'}</span>
                    </div>
                  {/each}
                </div>
              </div>
            {/if}
          </div>

          <!-- Mapa -->
          <div>
            {#await import('$lib/components/Mapa/MapaBase.svelte') then MapaModule}
              <MapaModule.default height="500px" onMapReady={onMapReady} />
            {/await}
          </div>
        </div>
      {/if}
    </div>
  </section>
</div>

<style>
  :global(.ponto-rota) {
    display: flex; align-items: center; justify-content: center;
    width: 24px; height: 24px; border-radius: 50%;
    background: #059669; color: white; font-size: 12px; font-weight: 700;
    border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }
  :global(.ponto-rota.inicio) { background: #2563eb; }
  :global(.ponto-rota.fim) { background: #dc2626; }
</style>
