<script lang="ts">
  interface LocalDescarte {
    id: string;
    nome: string;
    endereco: string;
    tipos_residuo: string[];
    horarios: Record<string, string>;
    telefone: string | null;
    avaliacao_media: number;
    total_avaliacoes: number;
  }

  let {
    local,
    onFechar = () => {},
  }: {
    local: LocalDescarte;
    onFechar?: () => void;
  } = $props();

  const tipoLabels: Record<string, string> = {
    reciclavel: '♻️ Reciclável',
    organico: '🌱 Orgânico',
    eletronico: '💻 Eletrônico',
    oleo: '🛢️ Óleo',
    pilhas: '🔋 Pilhas',
    vidro: '🪟 Vidro',
    papel: '📄 Papel',
    metal: '🔩 Metal',
    plastico: '🧴 Plástico',
    verde: '🌿 Verde',
  };

  const diaLabels: Record<string, string> = {
    seg: 'Seg', ter: 'Ter', qua: 'Qua', qui: 'Qui', sex: 'Sex', sab: 'Sáb', dom: 'Dom',
  };

  function renderEstrelas(media: number): string {
    const cheias = Math.round(media);
    return '★'.repeat(cheias) + '☆'.repeat(5 - cheias);
  }
</script>

<div class="rounded-xl border border-surface-200 bg-white p-5 shadow-sm">
  <div class="flex items-start justify-between">
    <h3 class="text-lg font-bold text-surface-900">{local.nome}</h3>
    <button onclick={onFechar} class="text-surface-400 transition-colors hover:text-surface-600">✕</button>
  </div>

  <p class="mt-1 text-sm text-surface-600">📍 {local.endereco}</p>

  {#if local.telefone}
    <p class="mt-1 text-sm text-surface-600">📞 {local.telefone}</p>
  {/if}

  <!-- Tipos de resíduo -->
  <div class="mt-3 flex flex-wrap gap-1.5">
    {#each local.tipos_residuo as tipo}
      <span class="rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-medium text-emerald-700">
        {tipoLabels[tipo] || tipo}
      </span>
    {/each}
  </div>

  <!-- Horários -->
  {#if Object.keys(local.horarios).length > 0}
    <div class="mt-3">
      <p class="text-xs font-semibold uppercase tracking-wider text-surface-500">Horários</p>
      <div class="mt-1 flex flex-wrap gap-1">
        {#each Object.entries(local.horarios) as [dia, horario]}
          <span class="rounded bg-surface-100 px-2 py-0.5 text-xs text-surface-700">
            <strong>{diaLabels[dia] || dia}:</strong> {horario}
          </span>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Avaliação -->
  <div class="mt-3 flex items-center gap-2">
    <span class="text-amber-500">{renderEstrelas(local.avaliacao_media)}</span>
    <span class="text-sm font-medium text-surface-700">{local.avaliacao_media}</span>
    <span class="text-xs text-surface-400">({local.total_avaliacoes} avaliações)</span>
  </div>
</div>
