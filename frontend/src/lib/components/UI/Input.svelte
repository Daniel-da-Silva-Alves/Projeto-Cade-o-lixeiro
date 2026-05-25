<script lang="ts">
  interface Props {
    label: string;
    name: string;
    type?: 'text' | 'password' | 'email' | 'number' | 'tel' | 'search' | 'url';
    placeholder?: string;
    value?: string;
    error?: string;
    required?: boolean;
    disabled?: boolean;
    maxlength?: number;
    oninput?: (e: Event) => void;
    class?: string;
  }

  let {
    label,
    name,
    type = 'text',
    placeholder = '',
    value = $bindable(''),
    error = '',
    required = false,
    disabled = false,
    maxlength,
    oninput,
    class: className = '',
  }: Props = $props();
</script>

<div class="space-y-1.5 {className}">
  <label for={name} class="block text-sm font-medium text-surface-700">
    {label}
    {#if required}
      <span class="text-danger-500">*</span>
    {/if}
  </label>
  <input
    id={name}
    {name}
    {type}
    {placeholder}
    {required}
    {disabled}
    {maxlength}
    bind:value
    {oninput}
    class="w-full rounded-lg border px-3 py-2 text-sm text-surface-800 transition-all
      placeholder:text-surface-200/60
      focus:outline-none focus:ring-2 focus:ring-offset-1
      {error
        ? 'border-danger-500 focus:ring-danger-500/30'
        : 'border-surface-200 focus:border-primary-500 focus:ring-primary-500/30'}
      disabled:bg-surface-100 disabled:cursor-not-allowed"
  />
  {#if error}
    <p class="text-xs text-danger-500">{error}</p>
  {/if}
</div>
