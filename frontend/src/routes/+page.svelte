<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import WidgetTop3 from '$lib/components/WidgetTop3.svelte';
  import MapaRastreamento from '$lib/components/MapaRastreamento.svelte';
  import LegendaCaminhoes from '$lib/components/LegendaCaminhoes.svelte';
  import IndicadorConexao from '$lib/components/IndicadorConexao.svelte';
  import {
    getCaminhoes,
    isConectado,
    conectarTracking,
    desconectarTracking,
    iniciarPing,
    pararPing,
  } from '$lib/stores/tracking.svelte';

  let mapaRef: MapaRastreamento;

  const features = [
    {
      icon: '🕐',
      title: 'Horários de Passagem',
      description: 'Consulte os horários e dias de passagem do caminhão no seu bairro.',
      href: '/horarios',
    },
    {
      icon: '♻️',
      title: 'Locais de Descarte',
      description: 'Encontre ecopontos e locais de descarte consciente próximos de você.',
      href: '/descarte',
    },
    {
      icon: '📢',
      title: 'Denúncias',
      description: 'Denuncie irregularidades ambientais de forma anônima e acompanhe o status.',
      href: '/denunciar',
    },
    {
      icon: '🏆',
      title: 'Ranking de Bairros',
      description: 'Veja quais bairros são os mais sustentáveis de Manaus.',
      href: '/ranking',
    },
    {
      icon: '🗺️',
      title: 'Rastreamento',
      description: 'Acompanhe a posição dos caminhões de coleta em tempo real no mapa.',
      href: '/',
    },
    {
      icon: 'ℹ️',
      title: 'Sobre',
      description: 'Conheça o projeto, a equipe e a tecnologia por trás do Cadê o Lixeiro.',
      href: '/sobre',
    },
  ];

  onMount(() => {
    conectarTracking();
    iniciarPing();
  });

  onDestroy(() => {
    desconectarTracking();
    pararPing();
  });

  function selecionarCaminhao(truckId: string) {
    mapaRef?.focarCaminhao(truckId);
  }
</script>

<svelte:head>
  <title>Cadê o Lixeiro? — Rastreamento em Tempo Real</title>
  <meta name="description" content="Acompanhe em tempo real a posição dos caminhões de coleta de Manaus. Consulte horários, locais de descarte e denuncie irregularidades." />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</svelte:head>

<div class="flex flex-col">
  <!-- Hero Section -->
  <section class="bg-gradient-to-br from-primary-700 via-primary-600 to-primary-800 px-4 py-12 text-white sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl text-center">
      <h1 class="text-3xl font-extrabold tracking-tight sm:text-4xl lg:text-5xl">
        🚛 Cadê o Lixeiro?
      </h1>
      <p class="mx-auto mt-4 max-w-2xl text-lg text-primary-100 sm:text-xl">
        Acompanhe em tempo real os caminhões de coleta em Manaus.
        Consulte horários, locais de descarte e ajude a manter sua cidade limpa.
      </p>
    </div>
  </section>

  <!-- Mapa de Rastreamento -->
  <section class="px-4 py-8 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <!-- Indicador de conexão -->
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-lg font-bold text-surface-800">📡 Rastreamento ao Vivo</h2>
        <IndicadorConexao conectado={isConectado()} />
      </div>

      <!-- Layout: Mapa + Legenda -->
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-4">
        <div class="lg:col-span-3">
          <MapaRastreamento
            bind:this={mapaRef}
            caminhoes={getCaminhoes()}
            height="500px"
            onCaminhaoClick={selecionarCaminhao}
          />
        </div>
        <div class="lg:col-span-1">
          <LegendaCaminhoes
            caminhoes={getCaminhoes()}
            onSelecionar={selecionarCaminhao}
          />
        </div>
      </div>
    </div>
  </section>

  <!-- Ranking Widget + Features -->
  <section class="bg-surface-50 px-4 py-12 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <!-- Widget Top3 -->
        <div class="lg:col-span-1">
          <WidgetTop3 />
        </div>

        <!-- Features Grid -->
        <div class="lg:col-span-2">
          <h2 class="mb-6 text-2xl font-bold text-surface-800">
            O que você pode fazer
          </h2>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {#each features as feature}
              <a
                href={feature.href}
                class="group rounded-xl border border-surface-200 bg-white p-5 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-md"
              >
                <span class="text-3xl">{feature.icon}</span>
                <h3 class="mt-2 text-base font-semibold text-surface-800 group-hover:text-primary-600">
                  {feature.title}
                </h3>
                <p class="mt-1 text-sm leading-relaxed text-surface-600">
                  {feature.description}
                </p>
              </a>
            {/each}
          </div>
        </div>
      </div>
    </div>
  </section>
</div>
