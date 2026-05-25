<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { Map as LeafletMap, LatLngExpression } from 'leaflet';

  let {
    center = [-3.1190, -60.0217] as LatLngExpression,
    zoom = 12,
    height = '500px',
    showGPS = false,
    onMapReady = (map: LeafletMap) => {},
  }: {
    center?: LatLngExpression;
    zoom?: number;
    height?: string;
    showGPS?: boolean;
    onMapReady?: (map: LeafletMap) => void;
  } = $props();

  let mapContainer: HTMLDivElement;
  let map: LeafletMap | null = $state(null);
  let L: any = null;

  onMount(async () => {
    // Dynamic import for SSR safety
    L = await import('leaflet');

    map = L.map(mapContainer, {
      zoomControl: true,
      attributionControl: true,
    }).setView(center, zoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);

    // GPS do cidadão
    if (showGPS && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          if (!map || !L) return;
          const latlng: LatLngExpression = [pos.coords.latitude, pos.coords.longitude];
          L.marker(latlng, {
            icon: L.divIcon({
              className: 'gps-marker',
              html: '<div class="gps-marker-dot"></div>',
              iconSize: [20, 20],
              iconAnchor: [10, 10],
            }),
          })
            .addTo(map)
            .bindPopup('📍 Sua localização');
        },
        () => {
          // GPS denied — silent fail
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    }

    onMapReady(map);
  });

  onDestroy(() => {
    if (map) {
      map.remove();
      map = null;
    }
  });
</script>

<div
  bind:this={mapContainer}
  class="mapa-base w-full rounded-xl border border-surface-200 shadow-sm"
  style="height: {height};"
></div>

<style>
  :global(.gps-marker-dot) {
    width: 16px;
    height: 16px;
    background: #3b82f6;
    border: 3px solid white;
    border-radius: 50%;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3), 0 2px 4px rgba(0,0,0,0.2);
    animation: pulse-gps 2s infinite;
  }

  @keyframes pulse-gps {
    0%, 100% { box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3), 0 2px 4px rgba(0,0,0,0.2); }
    50% { box-shadow: 0 0 0 8px rgba(59, 130, 246, 0.1), 0 2px 4px rgba(0,0,0,0.2); }
  }

  :global(.leaflet-container) {
    font-family: inherit;
    border-radius: 0.75rem;
  }
</style>
