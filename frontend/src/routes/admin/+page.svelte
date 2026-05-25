<script lang="ts">
  import { onMount } from 'svelte';
  import { getAuth } from '$lib/stores/auth.svelte';

  const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';
  const auth = getAuth();

  let kpis = $state<any>(null);
  let denunciasPorStatus = $state<any[]>([]);
  let denunciasPorBairro = $state<any[]>([]);
  let carregando = $state(true);

  onMount(async () => {
    if (!auth.token) return;
    await Promise.all([
      carregarKPIs(),
      carregarDenunciasPorStatus(),
      carregarDenunciasPorBairro(),
    ]);
    carregando = false;
  });

  async function carregarKPIs() {
    try {
      const res = await fetch(`${API_URL}/api/admin/kpis`, {
        headers: { 'Authorization': `Bearer ${auth.token}` },
      });
      if (res.ok) kpis = await res.json();
    } catch { /* silent */ }
  }

  async function carregarDenunciasPorStatus() {
    try {
      const res = await fetch(`${API_URL}/api/admin/denuncias-por-status`, {
        headers: { 'Authorization': `Bearer ${auth.token}` },
      });
      if (res.ok) {
        const data = await res.json();
        denunciasPorStatus = data.dados;
      }
    } catch { /* silent */ }
  }

  async function carregarDenunciasPorBairro() {
    try {
      const res = await fetch(`${API_URL}/api/admin/denuncias-por-bairro`, {
        headers: { 'Authorization': `Bearer ${auth.token}` },
      });
      if (res.ok) {
        const data = await res.json();
        denunciasPorBairro = data.dados;
      }
    } catch { /* silent */ }
  }

  const statusColors: Record<string, string> = {
    pendente: '#f59e0b',
    em_analise: '#3b82f6',
    resolvida: '#059669',
    rejeitada: '#dc2626',
  };

  const statusLabels: Record<string, string> = {
    pendente: 'Pendente',
    em_analise: 'Em Analise',
    resolvida: 'Resolvida',
    rejeitada: 'Rejeitada',
  };
</script>

<svelte:head>
  <title>Dashboard Admin — Cade o Lixeiro?</title>
  <meta name="description" content="Painel administrativo com KPIs, estatisticas e gestao do sistema." />
</svelte:head>

{#if !auth.autenticado}
  <div class="flex min-h-[60vh] items-center justify-center">
    <div class="text-center">
      <span class="text-5xl">🔒</span>
      <p class="mt-4 text-lg font-medium text-surface-700">Acesso restrito</p>
      <p class="mt-1 text-sm text-surface-500">Faca login como administrador para acessar.</p>
      <a href="/coletor" class="mt-4 inline-block rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white">
        Fazer Login
      </a>
    </div>
  </div>
{:else}
  <div class="flex flex-col">
    <!-- Header -->
    <section class="bg-gradient-to-br from-slate-800 to-slate-900 px-4 py-8 text-white sm:px-6">
      <div class="mx-auto max-w-7xl">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold">Dashboard Administrativo</h1>
            <p class="mt-1 text-slate-300">Visao geral do sistema</p>
          </div>
          <a
            href="/admin/"
            target="_blank"
            class="rounded-lg bg-slate-700 px-4 py-2 text-sm font-semibold text-white transition-all hover:bg-slate-600"
          >
            SQLAdmin (CRUD)
          </a>
        </div>
      </div>
    </section>

    <!-- KPIs -->
    <section class="px-4 py-6 sm:px-6">
      <div class="mx-auto max-w-7xl">
        {#if carregando}
          <div class="flex items-center justify-center py-12">
            <svg class="h-8 w-8 animate-spin text-primary-600" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
          </div>
        {:else if kpis}
          <div class="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            <!-- KPI: Caminhoes -->
            <div class="rounded-xl border border-surface-200 bg-white p-5 shadow-sm">
              <div class="text-2xl">🚛</div>
              <p class="mt-2 text-2xl font-bold text-surface-900">{kpis.caminhoes.online}/{kpis.caminhoes.total}</p>
              <p class="text-xs text-surface-500">Caminhoes Online</p>
            </div>

            <!-- KPI: Denuncias Pendentes -->
            <div class="rounded-xl border border-surface-200 bg-white p-5 shadow-sm">
              <div class="text-2xl">⚠️</div>
              <p class="mt-2 text-2xl font-bold text-amber-600">{kpis.denuncias.pendentes}</p>
              <p class="text-xs text-surface-500">Denuncias Pendentes</p>
            </div>

            <!-- KPI: Denuncias Total -->
            <div class="rounded-xl border border-surface-200 bg-white p-5 shadow-sm">
              <div class="text-2xl">📢</div>
              <p class="mt-2 text-2xl font-bold text-surface-900">{kpis.denuncias.total}</p>
              <p class="text-xs text-surface-500">Denuncias Total</p>
            </div>

            <!-- KPI: Rotas -->
            <div class="rounded-xl border border-surface-200 bg-white p-5 shadow-sm">
              <div class="text-2xl">🗺️</div>
              <p class="mt-2 text-2xl font-bold text-surface-900">{kpis.rotas_ativas}</p>
              <p class="text-xs text-surface-500">Rotas Ativas</p>
            </div>

            <!-- KPI: Locais -->
            <div class="rounded-xl border border-surface-200 bg-white p-5 shadow-sm">
              <div class="text-2xl">♻️</div>
              <p class="mt-2 text-2xl font-bold text-surface-900">{kpis.locais_descarte}</p>
              <p class="text-xs text-surface-500">Locais Descarte</p>
            </div>

            <!-- KPI: Bairros -->
            <div class="rounded-xl border border-surface-200 bg-white p-5 shadow-sm">
              <div class="text-2xl">📍</div>
              <p class="mt-2 text-2xl font-bold text-surface-900">{kpis.bairros}</p>
              <p class="text-xs text-surface-500">Bairros</p>
            </div>
          </div>

          <!-- Graficos -->
          <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <!-- Denuncias por Status -->
            <div class="rounded-xl border border-surface-200 bg-white p-5 shadow-sm">
              <h3 class="mb-4 text-sm font-semibold uppercase tracking-wider text-surface-500">
                Denuncias por Status
              </h3>
              {#if denunciasPorStatus.length > 0}
                <div class="space-y-3">
                  {#each denunciasPorStatus as item}
                    {@const total = denunciasPorStatus.reduce((s, i) => s + i.total, 0) || 1}
                    {@const pct = Math.round((item.total / total) * 100)}
                    <div>
                      <div class="mb-1 flex items-center justify-between text-sm">
                        <span class="font-medium text-surface-700">
                          {statusLabels[item.status] || item.status}
                        </span>
                        <span class="text-surface-500">{item.total} ({pct}%)</span>
                      </div>
                      <div class="h-3 overflow-hidden rounded-full bg-surface-100">
                        <div
                          class="h-full rounded-full transition-all"
                          style="width: {pct}%; background-color: {statusColors[item.status] || '#6b7280'}"
                        ></div>
                      </div>
                    </div>
                  {/each}
                </div>
              {:else}
                <p class="text-sm text-surface-400">Nenhuma denuncia registrada.</p>
              {/if}
            </div>

            <!-- Denuncias por Bairro -->
            <div class="rounded-xl border border-surface-200 bg-white p-5 shadow-sm">
              <h3 class="mb-4 text-sm font-semibold uppercase tracking-wider text-surface-500">
                Top Bairros com Denuncias
              </h3>
              {#if denunciasPorBairro.length > 0}
                <div class="space-y-2">
                  {#each denunciasPorBairro as item, i}
                    {@const max = denunciasPorBairro[0]?.total || 1}
                    {@const pct = Math.round((item.total / max) * 100)}
                    <div class="flex items-center gap-3">
                      <span class="w-5 text-right text-xs font-bold text-surface-400">{i + 1}</span>
                      <div class="flex-1">
                        <div class="mb-1 flex items-center justify-between text-sm">
                          <span class="font-medium text-surface-700">{item.bairro}</span>
                          <span class="text-surface-500">{item.total}</span>
                        </div>
                        <div class="h-2 overflow-hidden rounded-full bg-surface-100">
                          <div
                            class="h-full rounded-full bg-red-500 transition-all"
                            style="width: {pct}%"
                          ></div>
                        </div>
                      </div>
                    </div>
                  {/each}
                </div>
              {:else}
                <p class="text-sm text-surface-400">Nenhuma denuncia com bairro.</p>
              {/if}
            </div>
          </div>

          <!-- Links rapidos -->
          <div class="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <a href="/admin/" target="_blank" class="rounded-xl border border-surface-200 bg-white p-4 text-center shadow-sm transition-all hover:shadow-md">
              <span class="text-2xl">⚙️</span>
              <p class="mt-1 text-sm font-semibold text-surface-700">CRUD Admin</p>
            </a>
            <a href="/" class="rounded-xl border border-surface-200 bg-white p-4 text-center shadow-sm transition-all hover:shadow-md">
              <span class="text-2xl">📡</span>
              <p class="mt-1 text-sm font-semibold text-surface-700">Rastreamento</p>
            </a>
            <a href="/ranking" class="rounded-xl border border-surface-200 bg-white p-4 text-center shadow-sm transition-all hover:shadow-md">
              <span class="text-2xl">🏆</span>
              <p class="mt-1 text-sm font-semibold text-surface-700">Ranking</p>
            </a>
            <a href="/denunciar" class="rounded-xl border border-surface-200 bg-white p-4 text-center shadow-sm transition-all hover:shadow-md">
              <span class="text-2xl">📢</span>
              <p class="mt-1 text-sm font-semibold text-surface-700">Denuncias</p>
            </a>
          </div>
        {/if}
      </div>
    </section>
  </div>
{/if}
