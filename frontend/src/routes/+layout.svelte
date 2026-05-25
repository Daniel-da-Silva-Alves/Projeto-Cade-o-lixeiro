<script lang="ts">
  import './layout.css';
  import Header from '$lib/components/Layout/Header.svelte';
  import Footer from '$lib/components/Layout/Footer.svelte';
  import { inicializarAuth } from '$lib/stores/auth.svelte';
  import { onMount } from 'svelte';

  let { children } = $props();

  onMount(() => {
    inicializarAuth();

    // Registrar Service Worker para Push Notifications
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    }
  });
</script>

<svelte:head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="Cade o Lixeiro? — Rastreamento de caminhoes de coleta em Manaus. Horarios, locais de descarte, denuncias e ranking de bairros sustentaveis." />
  <meta name="theme-color" content="#059669" />
  <meta name="robots" content="index, follow" />
  <meta property="og:title" content="Cade o Lixeiro?" />
  <meta property="og:description" content="Acompanhe em tempo real os caminhoes de coleta em Manaus." />
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="pt_BR" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="manifest" href="/manifest.json" />
</svelte:head>

<a href="#main-content" class="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[100] focus:rounded-lg focus:bg-primary-600 focus:px-4 focus:py-2 focus:text-white focus:shadow-lg">
  Ir para conteudo principal
</a>

<div class="flex min-h-screen flex-col">
  <Header />

  <main id="main-content" class="flex-1">
    {@render children()}
  </main>

  <Footer />
</div>
