<script lang="ts">
  import { getAuth, logout } from '$lib/stores/auth.svelte';

  let mobileMenuOpen = $state(false);
  const auth = getAuth();

  const navLinks = [
    { href: '/', label: 'Mapa', icon: '🗺️' },
    { href: '/horarios', label: 'Horários', icon: '🕐' },
    { href: '/descarte', label: 'Descarte', icon: '♻️' },
    { href: '/denunciar', label: 'Denunciar', icon: '📢' },
    { href: '/ranking', label: 'Ranking', icon: '🏆' },
    { href: '/sobre', label: 'Sobre', icon: 'ℹ️' },
  ];

  function toggleMenu() {
    mobileMenuOpen = !mobileMenuOpen;
  }

  async function handleLogout() {
    mobileMenuOpen = false;
    await logout();
  }
</script>

<header class="sticky top-0 z-50 border-b border-surface-200 bg-white/80 backdrop-blur-lg">
  <nav class="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8" aria-label="Navegacao principal">
    <!-- Logo -->
    <a href="/" class="flex items-center gap-2 text-lg font-bold text-primary-700 transition-colors hover:text-primary-600">
      <span class="text-2xl">🚛</span>
      <span class="hidden sm:inline">Cadê o Lixeiro?</span>
    </a>

    <!-- Desktop Nav -->
    <div class="hidden items-center gap-1 md:flex">
      {#each navLinks as link}
        <a
          href={link.href}
          class="rounded-lg px-3 py-2 text-sm font-medium text-surface-700 transition-all hover:bg-primary-50 hover:text-primary-700"
        >
          <span class="mr-1">{link.icon}</span>
          {link.label}
        </a>
      {/each}
    </div>

    <!-- Auth Buttons (Desktop) -->
    <div class="hidden items-center gap-2 md:flex">
      {#if auth.autenticado}
        <span class="text-sm font-medium text-surface-600">
          👤 {auth.usuario?.nome}
        </span>
        <a
          href="/coletor"
          class="rounded-lg bg-primary-50 px-3 py-2 text-sm font-semibold text-primary-700 transition-all hover:bg-primary-100"
        >
          Painel
        </a>
        <button
          onclick={handleLogout}
          class="rounded-lg border border-red-200 px-3 py-2 text-sm font-semibold text-red-600 transition-all hover:bg-red-50"
        >
          Sair
        </button>
      {:else}
        <a
          href="/coletor"
          class="rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-primary-700 hover:shadow-md"
        >
          Área do Motorista
        </a>
      {/if}
    </div>

    <!-- Mobile Menu Button -->
    <button
      onclick={toggleMenu}
      class="inline-flex items-center justify-center rounded-lg p-2 text-surface-700 transition-colors hover:bg-surface-100 md:hidden"
      aria-label={mobileMenuOpen ? 'Fechar menu' : 'Abrir menu'}
      aria-expanded={mobileMenuOpen}
    >
      {#if mobileMenuOpen}
        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      {:else}
        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      {/if}
    </button>
  </nav>

  <!-- Mobile Menu -->
  {#if mobileMenuOpen}
    <div class="slide-down border-t border-surface-200 bg-white md:hidden" role="navigation" aria-label="Menu mobile">
      <div class="space-y-1 px-4 py-3">
        {#each navLinks as link}
          <a
            href={link.href}
            onclick={() => (mobileMenuOpen = false)}
            class="block rounded-lg px-3 py-2 text-base font-medium text-surface-700 transition-colors hover:bg-primary-50 hover:text-primary-700"
          >
            <span class="mr-2">{link.icon}</span>
            {link.label}
          </a>
        {/each}

        {#if auth.autenticado}
          <div class="mt-2 border-t border-surface-200 pt-2">
            <span class="block px-3 py-1 text-sm text-surface-500">
              👤 {auth.usuario?.nome}
            </span>
            <a
              href="/coletor"
              onclick={() => (mobileMenuOpen = false)}
              class="mt-1 block rounded-lg bg-primary-50 px-3 py-2 text-center text-base font-semibold text-primary-700 transition-colors hover:bg-primary-100"
            >
              Painel do Motorista
            </a>
            <button
              onclick={handleLogout}
              class="mt-1 w-full rounded-lg border border-red-200 px-3 py-2 text-center text-base font-semibold text-red-600 transition-colors hover:bg-red-50"
            >
              Sair
            </button>
          </div>
        {:else}
          <a
            href="/coletor"
            onclick={() => (mobileMenuOpen = false)}
            class="mt-2 block rounded-lg bg-primary-600 px-3 py-2 text-center text-base font-semibold text-white transition-colors hover:bg-primary-700"
          >
            Área do Motorista
          </a>
        {/if}
      </div>
    </div>
  {/if}
</header>
