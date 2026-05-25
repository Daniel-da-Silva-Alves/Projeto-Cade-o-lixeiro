<script lang="ts">
  interface CaminhaoPos {
    truck_id: string;
    latitude: number | null;
    longitude: number | null;
    endereco: string | null;
    status: 'online' | 'offline';
    timestamp: string;
  }

  let {
    caminhoes = new Map(),
    onSelecionar = (truckId: string) => {},
  }: {
    caminhoes: Map<string, CaminhaoPos>;
    onSelecionar?: (truckId: string) => void;
  } = $props();

  let arr = $derived(Array.from(caminhoes.values()));
  let online = $derived(arr.filter(c => c.status === 'online'));
  let offline = $derived(arr.filter(c => c.status === 'offline'));

  function tempoAtras(ts: string): string {
    const diff = Date.now() - new Date(ts).getTime();
    const min = Math.floor(diff / 60000);
    if (min < 1) return 'agora';
    if (min < 60) return `${min}min atrás`;
    return `${Math.floor(min / 60)}h atrás`;
  }
</script>

<div class="rounded-xl border border-surface-200 bg-white shadow-sm">
  <div class="border-b border-surface-200 px-4 py-3">
    <h3 class="text-sm font-semibold uppercase tracking-wider text-surface-500">
      🚛 Caminhões ({online.length} online)
    </h3>
  </div>

  {#if arr.length === 0}
    <div class="px-4 py-6 text-center">
      <span class="text-3xl">📭</span>
      <p class="mt-2 text-sm text-surface-500">Nenhum caminhão ativo no momento.</p>
    </div>
  {:else}
    <div class="max-h-[300px] overflow-y-auto">
      {#each online as cam}
        <button
          onclick={() => onSelecionar(cam.truck_id)}
          class="flex w-full items-center gap-3 border-b border-surface-50 px-4 py-3 text-left transition-colors hover:bg-surface-50"
        >
          <span class="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-sm">🚛</span>
          <div class="flex-1">
            <p class="text-sm font-semibold text-surface-900">{cam.truck_id}</p>
            {#if cam.endereco}
              <p class="text-xs text-surface-500 truncate">{cam.endereco}</p>
            {:else}
              <p class="text-xs text-surface-400">Aguardando localização...</p>
            {/if}
          </div>
          <div class="text-right">
            <span class="text-xs text-emerald-600 font-medium">● Online</span>
            <p class="text-xs text-surface-400">{tempoAtras(cam.timestamp)}</p>
          </div>
        </button>
      {/each}

      {#each offline as cam}
        <button
          onclick={() => onSelecionar(cam.truck_id)}
          class="flex w-full items-center gap-3 border-b border-surface-50 px-4 py-3 text-left opacity-50 transition-colors hover:bg-surface-50"
        >
          <span class="flex h-8 w-8 items-center justify-center rounded-full bg-surface-100 text-sm">🚛</span>
          <div class="flex-1">
            <p class="text-sm font-medium text-surface-600">{cam.truck_id}</p>
            <p class="text-xs text-surface-400">Offline</p>
          </div>
          <span class="text-xs text-surface-400">● Offline</span>
        </button>
      {/each}
    </div>
  {/if}
</div>
