<script lang="ts">
  interface Rota {
    id: string; rota_id: string; bairro: string; caminhao: string;
    tipo_coleta: string; dias_semana: string[];
    endereco_inicio: string | null; endereco_fim: string | null;
  }

  let {
    rotas = [],
    rotaSelecionada = $bindable<string | null>(null),
    onSelecionar = (id: string) => {},
  }: {
    rotas: Rota[];
    rotaSelecionada?: string | null;
    onSelecionar?: (id: string) => void;
  } = $props();

  const tipoLabels: Record<string, string> = {
    geral: '🚛 Geral',
    organico: '🌱 Orgânico',
    reciclavel: '♻️ Reciclável',
    perigoso: '☢️ Perigoso',
    verde: '🌿 Verde',
  };

  const diaLabels: Record<string, string> = {
    seg: 'Seg', ter: 'Ter', qua: 'Qua', qui: 'Qui', sex: 'Sex', sab: 'Sáb', dom: 'Dom',
  };
</script>

{#if rotas.length === 0}
  <div class="rounded-xl border border-surface-200 bg-white p-6 text-center">
    <span class="text-3xl">📭</span>
    <p class="mt-2 text-sm text-surface-500">Nenhuma rota encontrada para os bairros selecionados.</p>
  </div>
{:else}
  <div class="overflow-hidden rounded-xl border border-surface-200 bg-white shadow-sm">
    <table class="w-full text-sm">
      <thead>
        <tr class="border-b border-surface-200 bg-surface-50">
          <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Rota</th>
          <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Bairro</th>
          <th class="hidden px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500 sm:table-cell">Tipo</th>
          <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Dias</th>
          <th class="hidden px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-surface-500 sm:table-cell">Mapa</th>
        </tr>
      </thead>
      <tbody>
        {#each rotas as rota}
          <tr
            class="cursor-pointer border-b border-surface-100 transition-colors hover:bg-surface-50"
            class:bg-primary-50={rotaSelecionada === rota.id}
            onclick={() => { rotaSelecionada = rota.id; onSelecionar(rota.id); }}
          >
            <td class="px-4 py-3 font-medium text-surface-900">{rota.rota_id}</td>
            <td class="px-4 py-3 text-surface-700">{rota.bairro}</td>
            <td class="hidden px-4 py-3 text-surface-600 sm:table-cell">
              {tipoLabels[rota.tipo_coleta] || rota.tipo_coleta}
            </td>
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                {#each rota.dias_semana as dia}
                  <span class="rounded bg-primary-100 px-1.5 py-0.5 text-xs font-medium text-primary-700">
                    {diaLabels[dia] || dia}
                  </span>
                {/each}
              </div>
            </td>
            <td class="hidden px-4 py-3 text-center sm:table-cell">
              <span class="text-primary-600">🗺️</span>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}
