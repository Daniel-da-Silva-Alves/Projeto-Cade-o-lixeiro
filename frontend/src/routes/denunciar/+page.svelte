<script lang="ts">
  import UploadFotos from '$lib/components/UploadFotos.svelte';
  import ConsultaStatus from '$lib/components/ConsultaStatus.svelte';

  const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

  let tipo = $state('');
  let descricao = $state('');
  let latitude = $state(-3.1190);
  let longitude = $state(-60.0217);
  let fotos = $state<File[]>([]);
  let enviando = $state(false);
  let sucesso = $state<string | null>(null);
  let erro = $state('');
  let tab = $state<'denunciar' | 'consultar'>('denunciar');
  let mapaComponente: any = $state(null);
  let L: any = null;
  let marcador: any = null;

  const tipos = [
    { value: 'descarte_ilegal', label: '🗑️ Descarte Ilegal', desc: 'Lixo descartado em local inadequado' },
    { value: 'area_contaminada', label: '☣️ Área Contaminada', desc: 'Solo ou água contaminados' },
    { value: 'incendio_criminoso', label: '🔥 Incêndio Criminoso', desc: 'Queimada intencional de resíduos' },
  ];

  async function onMapReady(map: any) {
    mapaComponente = map;
    L = await import('leaflet');

    // GPS
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          latitude = pos.coords.latitude;
          longitude = pos.coords.longitude;
          atualizarMarcador();
          mapaComponente.setView([latitude, longitude], 16);
        },
        () => { atualizarMarcador(); },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    } else {
      atualizarMarcador();
    }
  }

  function atualizarMarcador() {
    if (!mapaComponente || !L) return;
    if (marcador) marcador.remove();

    marcador = L.marker([latitude, longitude], {
      draggable: true,
      icon: L.divIcon({
        className: 'denuncia-marker',
        html: '<div class="denuncia-pin">📍</div>',
        iconSize: [30, 30],
        iconAnchor: [15, 30],
      }),
    }).addTo(mapaComponente)
      .bindPopup('Arraste para ajustar a localização')
      .openPopup();

    marcador.on('dragend', () => {
      const latlng = marcador.getLatLng();
      latitude = latlng.lat;
      longitude = latlng.lng;
    });
  }

  async function enviar() {
    if (!tipo) { erro = 'Selecione o tipo de denúncia.'; return; }
    if (!descricao.trim() || descricao.trim().length < 10) {
      erro = 'Descreva a ocorrência com pelo menos 10 caracteres.'; return;
    }

    enviando = true;
    erro = '';
    sucesso = null;

    try {
      const formData = new FormData();
      formData.append('tipo', tipo);
      formData.append('descricao', descricao.trim());
      formData.append('latitude', String(latitude));
      formData.append('longitude', String(longitude));
      fotos.forEach(f => formData.append('fotos', f));

      const res = await fetch(`${API_URL}/api/denuncias`, {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        sucesso = data.id_acompanhamento;
        // Reset form
        tipo = ''; descricao = ''; fotos = [];
      } else if (res.status === 429) {
        erro = 'Limite de denúncias atingido (5 por dia).';
      } else {
        const data = await res.json().catch(() => ({}));
        erro = data.detail || 'Erro ao enviar denúncia.';
      }
    } catch {
      erro = 'Erro de conexão. Tente novamente.';
    }
    enviando = false;
  }
</script>

<svelte:head>
  <title>Denunciar — Cadê o Lixeiro?</title>
  <meta name="description" content="Denuncie irregularidades ambientais em Manaus. Denúncia anônima com foto e localização no mapa." />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</svelte:head>

<div class="flex flex-col">
  <!-- Header -->
  <section class="bg-gradient-to-br from-red-600 to-orange-600 px-4 py-10 text-white sm:px-6 lg:px-8">
    <div class="mx-auto max-w-4xl text-center">
      <span class="mb-2 inline-block text-4xl">📢</span>
      <h1 class="text-3xl font-extrabold tracking-tight sm:text-4xl">Denúncias Ambientais</h1>
      <p class="mx-auto mt-2 max-w-xl text-base text-red-100">
        Denuncie de forma anônima irregularidades ambientais em Manaus.
      </p>
    </div>
  </section>

  <!-- Tabs -->
  <div class="border-b border-surface-200 bg-white">
    <div class="mx-auto flex max-w-4xl">
      <button
        onclick={() => { tab = 'denunciar'; }}
        class="px-6 py-3 text-sm font-semibold transition-colors"
        class:border-b-2={tab === 'denunciar'}
        class:border-primary-600={tab === 'denunciar'}
        class:text-primary-600={tab === 'denunciar'}
        class:text-surface-500={tab !== 'denunciar'}
      >📝 Nova Denúncia</button>
      <button
        onclick={() => { tab = 'consultar'; }}
        class="px-6 py-3 text-sm font-semibold transition-colors"
        class:border-b-2={tab === 'consultar'}
        class:border-primary-600={tab === 'consultar'}
        class:text-primary-600={tab === 'consultar'}
        class:text-surface-500={tab !== 'consultar'}
      >🔍 Consultar Status</button>
    </div>
  </div>

  <!-- Content -->
  <section class="px-4 py-6 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-4xl">
      {#if tab === 'consultar'}
        <ConsultaStatus />
      {:else}
        {#if sucesso}
          <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-center">
            <span class="text-4xl">✅</span>
            <h2 class="mt-3 text-xl font-bold text-emerald-800">Denúncia Registrada!</h2>
            <p class="mt-2 text-sm text-emerald-700">Seu ID de acompanhamento:</p>
            <p class="mt-1 rounded-lg bg-white px-4 py-2 font-mono text-2xl font-bold text-emerald-900 shadow-sm inline-block">{sucesso}</p>
            <p class="mt-3 text-xs text-emerald-600">Guarde este ID para consultar o status da denúncia.</p>
            <button
              onclick={() => { sucesso = null; }}
              class="mt-4 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700"
            >Nova Denúncia</button>
          </div>
        {:else}
          <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <!-- Formulário -->
            <div class="space-y-4">
              <!-- Tipo -->
              <div>
                <span class="mb-1 block text-xs font-semibold uppercase tracking-wider text-surface-500" id="tipo-label">Tipo de Ocorrencia *</span>
                <div class="space-y-2" role="radiogroup" aria-labelledby="tipo-label">
                  {#each tipos as t}
                    <label
                      class="flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition-all"
                      class:border-primary-500={tipo === t.value}
                      class:bg-primary-50={tipo === t.value}
                      class:border-surface-200={tipo !== t.value}
                    >
                      <input type="radio" bind:group={tipo} value={t.value} class="accent-primary-600" />
                      <div>
                        <p class="text-sm font-semibold text-surface-900">{t.label}</p>
                        <p class="text-xs text-surface-500">{t.desc}</p>
                      </div>
                    </label>
                  {/each}
                </div>
              </div>

              <!-- Descrição -->
              <div>
                <label for="descricao" class="mb-1 block text-xs font-semibold uppercase tracking-wider text-surface-500">Descrição *</label>
                <textarea
                  id="descricao"
                  bind:value={descricao}
                  rows="4"
                  placeholder="Descreva a ocorrência com detalhes..."
                  class="w-full rounded-lg border border-surface-200 bg-white px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200"
                ></textarea>
              </div>

              <!-- Fotos -->
              <UploadFotos bind:fotos />

              {#if erro}
                <p class="text-sm text-red-600">{erro}</p>
              {/if}

              <button
                onclick={enviar}
                disabled={enviando}
                class="w-full rounded-lg bg-red-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition-all hover:bg-red-700 disabled:opacity-50"
              >
                {enviando ? '⏳ Enviando...' : '📨 Enviar Denúncia'}
              </button>
            </div>

            <!-- Mapa -->
            <div>
              <span class="mb-1 block text-xs font-semibold uppercase tracking-wider text-surface-500">📍 Localizacao (arraste o marcador)</span>
              {#await import('$lib/components/Mapa/MapaBase.svelte') then MapaModule}
                <MapaModule.default height="400px" zoom={14} onMapReady={onMapReady} />
              {/await}
              <p class="mt-2 text-xs text-surface-400">
                Lat: {latitude.toFixed(4)} | Lon: {longitude.toFixed(4)}
              </p>
            </div>
          </div>
        {/if}
      {/if}
    </div>
  </section>
</div>

<style>
  :global(.denuncia-pin) {
    font-size: 24px;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
  }
</style>
