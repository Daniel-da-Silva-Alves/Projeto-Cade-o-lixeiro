<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { getAuth } from '$lib/stores/auth.svelte';
  import LoginForm from '$lib/components/LoginForm.svelte';
  import IndicadorConexao from '$lib/components/IndicadorConexao.svelte';
  import {
    isColetando,
    iniciarColeta,
    pararColeta,
  } from '$lib/stores/tracking.svelte';

  const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';
  const auth = getAuth();

  let minhaRota = $state<any>(null);
  let carregandoRota = $state(false);
  let erroRota = $state('');
  let mapaComponente: any = $state(null);
  let L: any = null;
  let marcadoresRota: any[] = [];
  let polyline: any = null;
  let posicaoMarker: any = null;

  async function carregarMinhaRota() {
    if (!auth.token) return;
    carregandoRota = true;
    erroRota = '';

    try {
      const res = await fetch(`${API_URL}/api/rotas/minha-rota`, {
        headers: { 'Authorization': `Bearer ${auth.token}` },
      });
      if (res.ok) {
        minhaRota = await res.json();
        desenharRota();
      } else if (res.status === 404) {
        erroRota = 'Nenhuma rota atribuída.';
      }
    } catch {
      erroRota = 'Erro ao carregar rota.';
    }
    carregandoRota = false;
  }

  function desenharRota() {
    if (!mapaComponente || !L || !minhaRota?.rotas?.length) return;

    const rota = minhaRota.rotas[0];
    if (!rota.pontos.length) return;

    const coords = rota.pontos.map((p: any) => [p.latitude, p.longitude]);

    // Polyline
    if (polyline) polyline.remove();
    polyline = L.polyline(coords, {
      color: '#059669',
      weight: 4,
      opacity: 0.8,
      dashArray: '10, 6',
    }).addTo(mapaComponente);

    // Marcadores
    marcadoresRota.forEach(m => m.remove());
    marcadoresRota = [];

    rota.pontos.forEach((ponto: any, i: number) => {
      const isFirst = i === 0;
      const isLast = i === rota.pontos.length - 1;
      const cor = isFirst ? '#2563eb' : isLast ? '#dc2626' : '#059669';

      const marker = L.marker([ponto.latitude, ponto.longitude], {
        icon: L.divIcon({
          className: 'ponto-motorista',
          html: `<div style="
            width:24px;height:24px;border-radius:50%;
            background:${cor};color:white;font-size:11px;font-weight:700;
            display:flex;align-items:center;justify-content:center;
            border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,0.3)
          ">${ponto.ordem}</div>`,
          iconSize: [24, 24],
          iconAnchor: [12, 12],
        }),
      }).addTo(mapaComponente)
        .bindPopup(`<strong>${ponto.endereco}</strong><br>🕐 ${ponto.horario_passagem || 'N/D'}`);

      marcadoresRota.push(marker);
    });

    mapaComponente.fitBounds(L.latLngBounds(coords), { padding: [40, 40] });
  }

  async function onMapReady(map: any) {
    mapaComponente = map;
    L = await import('leaflet');
    await carregarMinhaRota();

    // Observar posição do motorista
    if (navigator.geolocation) {
      navigator.geolocation.watchPosition(
        (pos) => {
          const { latitude, longitude } = pos.coords;
          if (posicaoMarker) {
            posicaoMarker.setLatLng([latitude, longitude]);
          } else {
            posicaoMarker = L.circleMarker([latitude, longitude], {
              radius: 10,
              fillColor: '#3b82f6',
              fillOpacity: 0.9,
              color: '#1d4ed8',
              weight: 3,
            }).addTo(mapaComponente)
              .bindPopup('📍 Minha posição');
          }
        },
        () => {},
        { enableHighAccuracy: true }
      );
    }
  }

  async function toggleColeta() {
    if (isColetando()) {
      pararColeta();
    } else {
      const truckId = minhaRota?.caminhao?.truck_id;
      if (truckId && auth.token) {
        await iniciarColeta(truckId, auth.token);
      }
    }
  }
</script>

<svelte:head>
  <title>Área do Motorista — Cadê o Lixeiro?</title>
  <meta name="description" content="Painel do motorista para compartilhar localização GPS e visualizar rota de coleta." />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</svelte:head>

{#if auth.carregando}
  <!-- Skeleton loader -->
  <div class="flex min-h-[60vh] items-center justify-center">
    <div class="text-center">
      <svg class="mx-auto h-8 w-8 animate-spin text-primary-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
      <p class="mt-3 text-sm text-surface-500">Verificando sessão...</p>
    </div>
  </div>
{:else if auth.autenticado}
  <div class="flex flex-col">
    <!-- Header do motorista -->
    <section class="bg-gradient-to-br from-emerald-600 to-green-700 px-4 py-8 text-white sm:px-6">
      <div class="mx-auto max-w-5xl">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold">Olá, {auth.usuario?.nome} 👋</h1>
            <p class="mt-1 text-emerald-100">Painel do motorista</p>
          </div>
          <IndicadorConexao conectado={isColetando()} />
        </div>
      </div>
    </section>

    <!-- Controles -->
    <section class="px-4 py-6 sm:px-6">
      <div class="mx-auto max-w-5xl">
        <!-- Cards de controle -->
        <div class="mb-6 grid gap-4 sm:grid-cols-3">
          <!-- Card: Coleta -->
          <div class="rounded-xl border border-surface-200 bg-white p-5 shadow-sm">
            <div class="mb-3 text-3xl">📍</div>
            <h2 class="text-lg font-semibold text-surface-900">
              {isColetando() ? 'Coleta Ativa' : 'Iniciar Coleta'}
            </h2>
            <p class="mt-1 text-sm text-surface-500">
              {isColetando()
                ? 'Sua localização está sendo compartilhada.'
                : 'Ative o GPS e compartilhe sua posição.'
              }
            </p>
            <button
              onclick={toggleColeta}
              disabled={!minhaRota?.caminhao}
              class="mt-4 w-full rounded-lg px-4 py-2.5 text-sm font-semibold text-white transition-all disabled:opacity-50"
              class:bg-red-600={isColetando()}
              class:hover:bg-red-700={isColetando()}
              class:bg-emerald-600={!isColetando()}
              class:hover:bg-emerald-700={!isColetando()}
            >
              {isColetando() ? '⏹️ Encerrar Coleta' : '▶️ Iniciar Coleta'}
            </button>
          </div>

          <!-- Card: Veículo -->
          <div class="rounded-xl border border-surface-200 bg-white p-5 shadow-sm">
            <div class="mb-3 text-3xl">🚛</div>
            <h2 class="text-lg font-semibold text-surface-900">Meu Veículo</h2>
            {#if minhaRota?.caminhao}
              <div class="mt-2 space-y-1 text-sm text-surface-600">
                <p><strong>ID:</strong> {minhaRota.caminhao.truck_id}</p>
                <p><strong>Placa:</strong> {minhaRota.caminhao.placa || '—'}</p>
                <p><strong>Modelo:</strong> {minhaRota.caminhao.modelo || '—'}</p>
              </div>
            {:else}
              <p class="mt-2 text-sm text-surface-400">Carregando...</p>
            {/if}
          </div>

          <!-- Card: Rota -->
          <div class="rounded-xl border border-surface-200 bg-white p-5 shadow-sm">
            <div class="mb-3 text-3xl">🗺️</div>
            <h2 class="text-lg font-semibold text-surface-900">Minha Rota</h2>
            {#if minhaRota?.rotas?.length}
              {@const rota = minhaRota.rotas[0]}
              <div class="mt-2 space-y-1 text-sm text-surface-600">
                <p><strong>Rota:</strong> {rota.rota_id}</p>
                <p><strong>Bairro:</strong> {rota.bairro}</p>
                <p><strong>Pontos:</strong> {rota.pontos.length}</p>
              </div>
            {:else if erroRota}
              <p class="mt-2 text-sm text-red-500">{erroRota}</p>
            {:else}
              <p class="mt-2 text-sm text-surface-400">Carregando...</p>
            {/if}
          </div>
        </div>

        <!-- Mapa com rota -->
        <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div class="lg:col-span-2">
            {#await import('$lib/components/Mapa/MapaBase.svelte') then MapaModule}
              <MapaModule.default height="450px" zoom={13} onMapReady={onMapReady} />
            {/await}
          </div>

          <!-- Pontos da rota -->
          <div class="lg:col-span-1">
            {#if minhaRota?.rotas?.[0]?.pontos?.length}
              <div class="rounded-xl border border-surface-200 bg-white p-4 shadow-sm">
                <h3 class="mb-3 text-sm font-semibold uppercase tracking-wider text-surface-500">
                  Pontos da Rota ({minhaRota.rotas[0].pontos.length})
                </h3>
                <div class="max-h-[380px] space-y-1.5 overflow-y-auto">
                  {#each minhaRota.rotas[0].pontos as ponto}
                    <button
                      onclick={() => {
                        if (mapaComponente) mapaComponente.setView([ponto.latitude, ponto.longitude], 16);
                      }}
                      class="flex w-full items-center gap-3 rounded-lg bg-surface-50 px-3 py-2 text-left text-sm transition-colors hover:bg-surface-100"
                    >
                      <span class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-600 text-xs font-bold text-white">{ponto.ordem}</span>
                      <span class="flex-1 text-surface-800">{ponto.endereco}</span>
                      <span class="text-xs font-medium text-emerald-700">{ponto.horario_passagem || ''}</span>
                    </button>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        </div>
      </div>
    </section>
  </div>
{:else}
  <!-- Login form -->
  <div class="flex min-h-[60vh] items-center justify-center px-4 py-12">
    <LoginForm />
  </div>
{/if}
