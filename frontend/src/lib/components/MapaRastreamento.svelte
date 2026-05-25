<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

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
    height = '500px',
    onCaminhaoClick = (truckId: string) => {},
  }: {
    caminhoes: Map<string, CaminhaoPos>;
    height?: string;
    onCaminhaoClick?: (truckId: string) => void;
  } = $props();

  let mapContainer: HTMLDivElement;
  let map: any = null;
  let L: any = null;
  let marcadores = new Map<string, any>();

  onMount(async () => {
    if (typeof window === 'undefined') return;

    L = await import('leaflet');
    await import('leaflet/dist/leaflet.css');

    map = L.map(mapContainer, {
      center: [-3.1190, -60.0217],
      zoom: 12,
      zoomControl: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap',
      maxZoom: 18,
    }).addTo(map);

    // GPS do cidadão
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const { latitude, longitude } = pos.coords;
          L.circleMarker([latitude, longitude], {
            radius: 8,
            fillColor: '#3b82f6',
            fillOpacity: 0.9,
            color: '#1d4ed8',
            weight: 2,
          }).addTo(map)
            .bindPopup('📍 Sua localização');
        },
        () => {},
        { enableHighAccuracy: true, timeout: 10000 }
      );
    }
  });

  onDestroy(() => {
    if (map) {
      map.remove();
      map = null;
    }
  });

  // Efeito reativo: atualizar marcadores quando caminhoes muda
  $effect(() => {
    if (!map || !L) return;

    const idsAtuais = new Set(caminhoes.keys());

    // Remover marcadores que não existem mais
    for (const [id, marker] of marcadores) {
      if (!idsAtuais.has(id)) {
        marker.remove();
        marcadores.delete(id);
      }
    }

    // Atualizar/criar marcadores
    for (const [truckId, cam] of caminhoes) {
      if (cam.latitude == null || cam.longitude == null) continue;

      const isOnline = cam.status === 'online';

      if (marcadores.has(truckId)) {
        // Atualizar posição com animação suave
        const marker = marcadores.get(truckId);
        const targetLatLng = L.latLng(cam.latitude, cam.longitude);
        marker.setLatLng(targetLatLng);

        // Atualizar ícone se status mudou
        marker.setIcon(_criarIcone(isOnline));
        marker.setPopupContent(_criarPopup(cam));
      } else {
        // Criar novo marcador
        const marker = L.marker([cam.latitude, cam.longitude], {
          icon: _criarIcone(isOnline),
        })
          .addTo(map)
          .bindPopup(_criarPopup(cam));

        marker.on('click', () => onCaminhaoClick(truckId));
        marcadores.set(truckId, marker);
      }
    }
  });

  function _criarIcone(online: boolean) {
    return L.divIcon({
      className: 'caminhao-marker',
      html: `<div class="caminhao-pin ${online ? 'online' : 'offline'}">🚛</div>`,
      iconSize: [36, 36],
      iconAnchor: [18, 18],
    });
  }

  function _criarPopup(cam: CaminhaoPos): string {
    const status = cam.status === 'online'
      ? '<span style="color:#059669">● Online</span>'
      : '<span style="color:#dc2626">● Offline</span>';

    return `
      <div style="min-width:150px">
        <strong>${cam.truck_id}</strong><br>
        ${status}<br>
        ${cam.endereco ? `📍 ${cam.endereco}<br>` : ''}
        <small>🕐 ${new Date(cam.timestamp).toLocaleTimeString('pt-BR')}</small>
      </div>
    `;
  }

  export function focarCaminhao(truckId: string) {
    const cam = caminhoes.get(truckId);
    if (cam?.latitude && cam?.longitude && map) {
      map.setView([cam.latitude, cam.longitude], 16);
      const marker = marcadores.get(truckId);
      if (marker) marker.openPopup();
    }
  }
</script>

<div bind:this={mapContainer} style="height: {height}; width: 100%;" class="rounded-xl overflow-hidden shadow-sm border border-surface-200"></div>

<style>
  :global(.caminhao-pin) {
    font-size: 24px;
    filter: drop-shadow(0 2px 6px rgba(0,0,0,0.3));
    transition: transform 0.3s ease;
  }
  :global(.caminhao-pin.online) {
    animation: pulse-truck 2s infinite;
  }
  :global(.caminhao-pin.offline) {
    opacity: 0.5;
    filter: grayscale(80%) drop-shadow(0 2px 4px rgba(0,0,0,0.2));
  }
  @keyframes pulse-truck {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }
</style>
