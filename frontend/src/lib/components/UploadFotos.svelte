<script lang="ts">
  let {
    fotos = $bindable<File[]>([]),
  }: {
    fotos?: File[];
  } = $props();

  let erro = $state('');
  let previews = $state<string[]>([]);

  function onArquivoSelecionado(e: Event) {
    const input = e.target as HTMLInputElement;
    if (!input.files) return;

    erro = '';
    const novos = Array.from(input.files);

    for (const f of novos) {
      if (!['image/jpeg', 'image/png', 'image/webp'].includes(f.type)) {
        erro = `${f.name}: formato inválido. Use JPG, PNG ou WEBP.`;
        return;
      }
      if (f.size > 5 * 1024 * 1024) {
        erro = `${f.name}: excede 5MB.`;
        return;
      }
    }

    const total = fotos.length + novos.length;
    if (total > 3) {
      erro = 'Máximo de 3 fotos.';
      return;
    }

    fotos = [...fotos, ...novos];
    // Gerar previews
    novos.forEach(f => {
      const reader = new FileReader();
      reader.onload = (ev) => {
        previews = [...previews, ev.target?.result as string];
      };
      reader.readAsDataURL(f);
    });

    input.value = '';
  }

  function remover(i: number) {
    fotos = fotos.filter((_, idx) => idx !== i);
    previews = previews.filter((_, idx) => idx !== i);
  }
</script>

<div>
  <span class="mb-1 block text-xs font-semibold uppercase tracking-wider text-surface-500">
    📷 Fotos (max. 3, ate 5MB cada)
  </span>

  {#if fotos.length < 3}
    <label class="flex cursor-pointer items-center justify-center rounded-lg border-2 border-dashed border-surface-300 bg-surface-50 p-6 transition-colors hover:border-primary-400 hover:bg-primary-50">
      <input
        type="file"
        accept="image/jpeg,image/png,image/webp"
        multiple
        onchange={onArquivoSelecionado}
        class="hidden"
      />
      <div class="text-center">
        <span class="text-3xl">📤</span>
        <p class="mt-1 text-sm text-surface-600">Clique para adicionar fotos</p>
        <p class="text-xs text-surface-400">JPG, PNG ou WEBP</p>
      </div>
    </label>
  {/if}

  {#if erro}
    <p class="mt-2 text-xs text-red-600">{erro}</p>
  {/if}

  {#if previews.length > 0}
    <div class="mt-3 flex gap-3">
      {#each previews as preview, i}
        <div class="group relative">
          <img src={preview} alt="Preview {i+1}" class="h-20 w-20 rounded-lg object-cover shadow-sm" />
          <button
            onclick={() => remover(i)}
            class="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white opacity-0 transition-opacity group-hover:opacity-100"
          >✕</button>
        </div>
      {/each}
    </div>
  {/if}
</div>
