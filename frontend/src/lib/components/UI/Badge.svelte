<script lang="ts">
  type BadgeVariant = 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'neutral';

  interface Props {
    variant?: BadgeVariant;
    text: string;
    class?: string;
  }

  let {
    variant = 'neutral',
    text,
    class: className = '',
  }: Props = $props();

  const variants: Record<BadgeVariant, string> = {
    primary: 'bg-primary-100 text-primary-700',
    success: 'bg-green-100 text-green-700',
    warning: 'bg-amber-100 text-amber-700',
    danger: 'bg-red-100 text-red-700',
    info: 'bg-blue-100 text-blue-700',
    neutral: 'bg-surface-200 text-surface-700',
  };
</script>

<span
  class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold {variants[variant]} {className}"
>
  {text}
</span>
