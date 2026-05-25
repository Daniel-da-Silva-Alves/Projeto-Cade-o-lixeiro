<script lang="ts">
  let { conectado = false }: { conectado: boolean } = $props();
</script>

<div class="flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold transition-all"
  class:bg-emerald-100={conectado}
  class:text-emerald-700={conectado}
  class:bg-red-100={!conectado}
  class:text-red-700={!conectado}
>
  <span class="relative flex h-2 w-2">
    {#if conectado}
      <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
    {/if}
    <span class="relative inline-flex h-2 w-2 rounded-full"
      class:bg-emerald-500={conectado}
      class:bg-red-500={!conectado}
    ></span>
  </span>
  {conectado ? '🟢 Ao vivo' : '🔴 Desconectado'}
</div>
