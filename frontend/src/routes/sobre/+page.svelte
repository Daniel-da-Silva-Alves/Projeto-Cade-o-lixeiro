<script lang="ts">
  const equipe = [
    { nome: 'Daniel Alves', papel: 'Desenvolvedor Full-Stack', emoji: '💻' },
  ];

  const funcionalidades = [
    { icon: '🗺️', titulo: 'Rastreamento em Tempo Real', desc: 'Acompanhe os caminhões de coleta no mapa com atualização ao vivo via WebSocket.' },
    { icon: '🕐', titulo: 'Horários de Passagem', desc: 'Consulte dias e horários de passagem do caminhão de lixo no seu bairro.' },
    { icon: '♻️', titulo: 'Locais de Descarte', desc: 'Encontre ecopontos, cooperativas e pontos de descarte consciente em Manaus.' },
    { icon: '📢', titulo: 'Denúncias Anônimas', desc: 'Denuncie irregularidades ambientais com fotos e localização no mapa.' },
    { icon: '🏆', titulo: 'Ranking de Bairros', desc: 'Gamificação por bairro: denúncias resolvidas e descartes corretos pontuam.' },
    { icon: '🔔', titulo: 'Notificações Push', desc: 'Receba alertas quando o caminhão de coleta estiver próximo do seu bairro.' },
  ];

  const stack = [
    { nome: 'SvelteKit 5', categoria: 'Frontend', cor: 'bg-orange-100 text-orange-700' },
    { nome: 'Tailwind CSS v4', categoria: 'Estilização', cor: 'bg-sky-100 text-sky-700' },
    { nome: 'FastAPI', categoria: 'Backend', cor: 'bg-emerald-100 text-emerald-700' },
    { nome: 'PostgreSQL + PostGIS', categoria: 'Banco de Dados', cor: 'bg-blue-100 text-blue-700' },
    { nome: 'Supabase', categoria: 'Infraestrutura', cor: 'bg-green-100 text-green-700' },
    { nome: 'Leaflet.js', categoria: 'Mapas', cor: 'bg-lime-100 text-lime-700' },
    { nome: 'WebSockets', categoria: 'Realtime', cor: 'bg-violet-100 text-violet-700' },
    { nome: 'SQLAlchemy 2.0', categoria: 'ORM', cor: 'bg-amber-100 text-amber-700' },
  ];
</script>

<svelte:head>
  <title>Sobre — Cadê o Lixeiro?</title>
  <meta name="description" content="Conheça o projeto Cadê o Lixeiro? — plataforma de rastreamento de caminhões de coleta em Manaus. Missão, funcionalidades, equipe e tecnologias." />
</svelte:head>

<div class="flex flex-col">
  <!-- Hero / Missão -->
  <section id="missao" class="bg-gradient-to-br from-primary-700 via-primary-600 to-emerald-700 px-4 py-16 text-white sm:px-6 lg:px-8">
    <div class="mx-auto max-w-4xl text-center">
      <span class="mb-4 inline-block text-5xl">🚛</span>
      <h1 class="text-3xl font-extrabold tracking-tight sm:text-4xl lg:text-5xl">
        Cadê o Lixeiro?
      </h1>
      <p class="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-primary-100">
        Uma plataforma civic-tech que conecta os cidadãos de Manaus ao serviço de coleta de lixo.
        Rastreamento em tempo real, horários de passagem, locais de descarte consciente,
        denúncias ambientais e ranking de sustentabilidade por bairro.
      </p>
      <div class="mt-8 flex flex-wrap justify-center gap-3">
        <span class="rounded-full bg-white/15 px-4 py-1.5 text-sm font-medium backdrop-blur-sm">📍 Manaus, AM</span>
        <span class="rounded-full bg-white/15 px-4 py-1.5 text-sm font-medium backdrop-blur-sm">🏘️ 63 bairros</span>
        <span class="rounded-full bg-white/15 px-4 py-1.5 text-sm font-medium backdrop-blur-sm">🌱 Sustentabilidade</span>
      </div>
    </div>
  </section>

  <!-- Funcionalidades -->
  <section id="funcionalidades" class="bg-white px-4 py-16 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="mb-12 text-center">
        <h2 class="text-2xl font-bold text-surface-900 sm:text-3xl">Funcionalidades</h2>
        <p class="mt-2 text-surface-500">Tudo o que você precisa para acompanhar a coleta na sua região.</p>
      </div>
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {#each funcionalidades as feat}
          <div class="group rounded-xl border border-surface-200 bg-white p-6 transition-all duration-200 hover:-translate-y-1 hover:shadow-lg">
            <span class="text-4xl">{feat.icon}</span>
            <h3 class="mt-3 text-lg font-semibold text-surface-900 group-hover:text-primary-600">{feat.titulo}</h3>
            <p class="mt-2 text-sm leading-relaxed text-surface-600">{feat.desc}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Equipe -->
  <section id="equipe" class="bg-surface-50 px-4 py-16 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-4xl">
      <div class="mb-12 text-center">
        <h2 class="text-2xl font-bold text-surface-900 sm:text-3xl">Equipe</h2>
        <p class="mt-2 text-surface-500">As pessoas por trás do projeto.</p>
      </div>
      <div class="flex flex-wrap justify-center gap-6">
        {#each equipe as membro}
          <div class="flex w-64 flex-col items-center rounded-xl border border-surface-200 bg-white p-6 text-center shadow-sm">
            <span class="text-5xl">{membro.emoji}</span>
            <h3 class="mt-4 text-lg font-semibold text-surface-900">{membro.nome}</h3>
            <p class="mt-1 text-sm text-surface-500">{membro.papel}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Stack Tecnológica -->
  <section id="stack" class="bg-white px-4 py-16 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-4xl">
      <div class="mb-12 text-center">
        <h2 class="text-2xl font-bold text-surface-900 sm:text-3xl">Stack Tecnológica</h2>
        <p class="mt-2 text-surface-500">Tecnologias de ponta para uma experiência moderna.</p>
      </div>
      <div class="flex flex-wrap justify-center gap-3">
        {#each stack as tech}
          <div class="flex items-center gap-2 rounded-full {tech.cor} px-4 py-2 text-sm font-medium transition-transform hover:scale-105">
            <span>{tech.nome}</span>
            <span class="text-xs opacity-60">({tech.categoria})</span>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Contato / GitHub -->
  <section id="contato" class="bg-gradient-to-br from-surface-800 to-surface-900 px-4 py-16 text-white sm:px-6 lg:px-8">
    <div class="mx-auto max-w-4xl text-center">
      <h2 class="text-2xl font-bold sm:text-3xl">Contribua com o Projeto</h2>
      <p class="mx-auto mt-4 max-w-xl text-surface-300">
        O Cadê o Lixeiro? é um projeto open-source. Contribuições, sugestões e feedback são bem-vindos!
      </p>
      <div class="mt-8 flex flex-wrap justify-center gap-4">
        <a
          href="https://github.com/daniel-alves/cade-o-lixeiro"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2 rounded-lg bg-white px-6 py-3 text-sm font-semibold text-surface-900 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
        >
          <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
          GitHub
        </a>
        <a
          href="mailto:contato@cadeolixeiro.com"
          class="inline-flex items-center gap-2 rounded-lg border border-white/20 bg-white/10 px-6 py-3 text-sm font-semibold text-white backdrop-blur-sm transition-all hover:-translate-y-0.5 hover:bg-white/20"
        >
          ✉️ Contato
        </a>
      </div>
    </div>
  </section>
</div>
