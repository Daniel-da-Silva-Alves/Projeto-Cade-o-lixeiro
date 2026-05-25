<script lang="ts">
  type ToastType = 'success' | 'error' | 'info' | 'warning';

  interface Props {
    message: string;
    type?: ToastType;
    visible?: boolean;
    duration?: number;
    onclose?: () => void;
  }

  let {
    message,
    type = 'info',
    visible = $bindable(true),
    duration = 5000,
    onclose,
  }: Props = $props();

  const icons: Record<ToastType, string> = {
    success: '✅',
    error: '❌',
    info: 'ℹ️',
    warning: '⚠️',
  };

  const colors: Record<ToastType, string> = {
    success: 'bg-primary-50 border-primary-300 text-primary-800',
    error: 'bg-red-50 border-red-300 text-red-800',
    info: 'bg-blue-50 border-blue-300 text-blue-800',
    warning: 'bg-amber-50 border-amber-300 text-amber-800',
  };

  $effect(() => {
    if (visible && duration > 0) {
      const timer = setTimeout(() => {
        visible = false;
        onclose?.();
      }, duration);
      return () => clearTimeout(timer);
    }
  });

  function close() {
    visible = false;
    onclose?.();
  }
</script>

{#if visible}
  <div
    class="fixed bottom-4 right-4 z-[100] flex max-w-sm items-start gap-3 rounded-lg border p-4 shadow-elevated animate-in slide-in-from-right {colors[type]}"
    role="alert"
  >
    <span class="text-lg">{icons[type]}</span>
    <p class="flex-1 text-sm font-medium">{message}</p>
    <button
      onclick={close}
      class="text-current opacity-50 transition-opacity hover:opacity-100"
      aria-label="Fechar"
    >
      ✕
    </button>
  </div>
{/if}
