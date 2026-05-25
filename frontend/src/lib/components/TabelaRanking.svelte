<script lang="ts">
  interface RankingItem {
    posicao: number;
    bairro: string;
    pontuacao: number;
    denuncias_resolvidas: number;
    descartes_corretos: number;
  }

  let { ranking = [], periodo = 'mensal' }: { ranking: RankingItem[]; periodo: string } = $props();

  function getMedalha(pos: number): string {
    if (pos === 1) return '🥇';
    if (pos === 2) return '🥈';
    if (pos === 3) return '🥉';
    return `${pos}º`;
  }
</script>

{#if ranking.length === 0}
  <div class="rounded-xl border border-surface-200 bg-white p-8 text-center">
    <span class="text-4xl">📊</span>
    <h3 class="mt-3 text-lg font-semibold text-surface-700">Ranking ainda sem dados</h3>
    <p class="mt-2 text-sm text-surface-500">
      {#if periodo === 'mensal'}
        Nenhuma denúncia resolvida ou descarte avaliado neste mês.
      {:else}
        Nenhum dado de ranking registrado ainda.
      {/if}
    </p>
    <p class="mt-1 text-xs text-surface-400">
      Os dados são atualizados automaticamente conforme a comunidade participa.
    </p>
  </div>
{:else}
  <div class="overflow-hidden rounded-xl border border-surface-200 bg-white shadow-sm">
    <table class="w-full">
      <thead>
        <tr class="border-b border-surface-200 bg-surface-50">
          <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">#</th>
          <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Bairro</th>
          <th class="px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-surface-500">Denúncias</th>
          <th class="px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-surface-500">Descartes</th>
          <th class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-surface-500">Pontos</th>
        </tr>
      </thead>
      <tbody>
        {#each ranking as item, i}
          <tr
            class="border-b border-surface-100 transition-colors hover:bg-surface-50"
            class:bg-amber-50={item.posicao <= 3}
          >
            <td class="px-4 py-3 text-lg font-bold">
              {getMedalha(item.posicao)}
            </td>
            <td class="px-4 py-3 font-medium text-surface-900">
              {item.bairro}
            </td>
            <td class="px-4 py-3 text-center text-sm text-surface-600">
              {item.denuncias_resolvidas}
            </td>
            <td class="px-4 py-3 text-center text-sm text-surface-600">
              {item.descartes_corretos}
            </td>
            <td class="px-4 py-3 text-right">
              <span class="inline-flex items-center rounded-full bg-primary-100 px-2.5 py-0.5 text-sm font-bold text-primary-700">
                {item.pontuacao}
              </span>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}
