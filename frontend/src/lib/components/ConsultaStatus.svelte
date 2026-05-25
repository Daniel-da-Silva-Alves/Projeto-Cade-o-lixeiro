<script lang="ts">
  const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

  let idBusca = $state('');
  let resultado = $state<any>(null);
  let carregando = $state(false);
  let erro = $state('');

  const statusCores: Record<string, string> = {
    pendente: 'bg-amber-100 text-amber-700',
    em_andamento: 'bg-blue-100 text-blue-700',
    resolvida: 'bg-emerald-100 text-emerald-700',
    descartada: 'bg-red-100 text-red-700',
  };

  async function consultar() {
    if (!idBusca.trim()) return;
    carregando = true;
    erro = '';
    resultado = null;

    try {
      const res = await fetch(`${API_URL}/api/denuncias/${idBusca.trim().toUpperCase()}`);
      if (res.ok) {
        resultado = await res.json();
      } else if (res.status === 404) {
        erro = 'Denúncia não encontrada. Verifique o ID.';
      } else {
        erro = 'Erro ao consultar. Tente novamente.';
      }
    } catch {
      erro = 'Erro de conexão. Tente novamente.';
    }
    carregando = false;
  }
</script>

<div class="rounded-xl border border-surface-200 bg-white p-6 shadow-sm">
  <h3 class="mb-4 text-lg font-bold text-surface-900">🔍 Consultar Denúncia</h3>

  <div class="flex gap-2">
    <input
      type="text"
      placeholder="DEN-2026-00001"
      bind:value={idBusca}
      class="flex-1 rounded-lg border border-surface-200 bg-white px-3 py-2 text-sm uppercase shadow-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200"
    />
    <button
      onclick={consultar}
      disabled={carregando}
      class="rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white transition-all hover:bg-primary-700 disabled:opacity-50"
    >
      {carregando ? '...' : 'Buscar'}
    </button>
  </div>

  {#if erro}
    <p class="mt-3 text-sm text-red-600">{erro}</p>
  {/if}

  {#if resultado}
    {@const d = resultado.denuncia}
    <div class="mt-4 space-y-3">
      <div class="flex items-center justify-between">
        <span class="font-mono text-sm font-bold text-surface-900">{d.id_acompanhamento}</span>
        <span class="rounded-full px-3 py-1 text-xs font-semibold {statusCores[d.status] || 'bg-surface-100 text-surface-700'}">
          {d.status_label}
        </span>
      </div>

      <div class="text-sm text-surface-600">
        <p><strong>Tipo:</strong> {d.tipo_label}</p>
        <p><strong>Descrição:</strong> {d.descricao}</p>
        {#if d.bairro}
          <p><strong>Bairro:</strong> {d.bairro}</p>
        {/if}
        <p><strong>Data:</strong> {new Date(d.data).toLocaleDateString('pt-BR')}</p>
      </div>

      <!-- Timeline -->
      {#if resultado.timeline.length > 0}
        <div class="mt-3">
          <p class="text-xs font-semibold uppercase tracking-wider text-surface-500">Timeline</p>
          <div class="mt-2 space-y-2">
            {#each resultado.timeline as evento}
              <div class="flex gap-3 text-sm">
                <span class="text-xs text-surface-400">{new Date(evento.data).toLocaleDateString('pt-BR')}</span>
                <span class="rounded-full px-2 py-0.5 text-xs {statusCores[evento.status_novo] || 'bg-surface-100'}">{evento.status_novo}</span>
                {#if evento.observacao}
                  <span class="text-surface-600">{evento.observacao}</span>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>
