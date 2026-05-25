/**
 * Cadê o Lixeiro? v2.0 — Store de Rastreamento em Tempo Real
 *
 * WebSocket client com reconexão automática, estado reativo via Svelte 5 runes.
 * Ref: RAT-1 SDD §4.3, RAT-2 SDD §2.2
 */

interface CaminhaoPos {
  truck_id: string;
  latitude: number | null;
  longitude: number | null;
  endereco: string | null;
  status: 'online' | 'offline';
  timestamp: string;
}

const WS_URL = (import.meta.env.PUBLIC_API_URL || 'http://localhost:8000')
  .replace('http://', 'ws://')
  .replace('https://', 'wss://');

const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

// --- Estado reativo (Svelte 5 runes) ---
let caminhoes = $state<Map<string, CaminhaoPos>>(new Map());
let conectado = $state(false);
let totalCidadaos = $state(0);

// --- WebSocket de cidadão ---
let ws: WebSocket | null = null;
let tentativas = 0;
const MAX_TENTATIVAS = 10;
const INTERVALO_RECONEXAO = 5000;

export function getCaminhoes() {
  return caminhoes;
}

export function isConectado() {
  return conectado;
}

export function conectarTracking() {
  if (typeof window === 'undefined') return; // SSR guard

  try {
    ws = new WebSocket(`${WS_URL}/ws/tracking`);
  } catch {
    _reconectar();
    return;
  }

  ws.onopen = () => {
    conectado = true;
    tentativas = 0;
    console.log('[WS] Conectado ao tracking.');
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);

      switch (msg.tipo) {
        case 'estado_inicial':
          // Recebe todos os caminhões online ao conectar
          const novoMapa = new Map<string, CaminhaoPos>();
          for (const c of msg.caminhoes) {
            novoMapa.set(c.truck_id, c);
          }
          caminhoes = novoMapa;
          break;

        case 'posicao_atualizada':
          caminhoes.set(msg.truck_id, {
            truck_id: msg.truck_id,
            latitude: msg.latitude,
            longitude: msg.longitude,
            endereco: msg.endereco || null,
            status: 'online',
            timestamp: msg.timestamp,
          });
          // Trigger reatividade
          caminhoes = new Map(caminhoes);
          break;

        case 'caminhao_online':
          if (!caminhoes.has(msg.truck_id)) {
            caminhoes.set(msg.truck_id, {
              truck_id: msg.truck_id,
              latitude: null,
              longitude: null,
              endereco: null,
              status: 'online',
              timestamp: new Date().toISOString(),
            });
            caminhoes = new Map(caminhoes);
          }
          break;

        case 'caminhao_offline':
          const c = caminhoes.get(msg.truck_id);
          if (c) {
            c.status = 'offline';
            caminhoes = new Map(caminhoes);
          }
          break;
      }
    } catch (e) {
      console.warn('[WS] Erro ao processar mensagem:', e);
    }
  };

  ws.onclose = () => {
    conectado = false;
    console.log('[WS] Desconectado.');
    _reconectar();
  };

  ws.onerror = () => {
    conectado = false;
  };
}

export function desconectarTracking() {
  if (ws) {
    ws.close();
    ws = null;
  }
  conectado = false;
}

function _reconectar() {
  if (tentativas < MAX_TENTATIVAS) {
    tentativas++;
    console.log(`[WS] Reconectando em ${INTERVALO_RECONEXAO / 1000}s... (tentativa ${tentativas}/${MAX_TENTATIVAS})`);
    setTimeout(conectarTracking, INTERVALO_RECONEXAO);
  } else {
    console.warn('[WS] Máximo de tentativas atingido.');
  }
}

// --- Ping keep-alive ---
let pingInterval: ReturnType<typeof setInterval> | null = null;

export function iniciarPing() {
  pingInterval = setInterval(() => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send('ping');
    }
  }, 30000); // 30s
}

export function pararPing() {
  if (pingInterval) {
    clearInterval(pingInterval);
    pingInterval = null;
  }
}

// --- Compartilhamento de localização (Motorista) ---
let watchId: number | null = null;
let driverWs: WebSocket | null = null;
let coletando = $state(false);

export function isColetando() {
  return coletando;
}

export async function iniciarColeta(truckId: string, token: string) {
  if (typeof window === 'undefined') return;

  // Abrir WebSocket autenticado
  try {
    driverWs = new WebSocket(`${WS_URL}/ws/driver/${truckId}?token=${token}`);
  } catch {
    console.error('[WS Driver] Erro ao conectar.');
    return;
  }

  driverWs.onopen = () => {
    coletando = true;
    console.log('[WS Driver] Conectado. Iniciando GPS...');

    // Iniciar GPS
    if (navigator.geolocation) {
      watchId = navigator.geolocation.watchPosition(
        (pos) => {
          if (driverWs?.readyState === WebSocket.OPEN) {
            driverWs.send(JSON.stringify({
              tipo: 'posicao',
              lat: pos.coords.latitude,
              lng: pos.coords.longitude,
            }));
          }
        },
        (err) => {
          console.warn('[GPS] Erro:', err.message);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 3000, // Cache de 3s para alinhar com anti-spam do server
        }
      );
    }
  };

  driverWs.onclose = () => {
    coletando = false;
    _limparGPS();
    console.log('[WS Driver] Desconectado.');
  };

  driverWs.onerror = () => {
    console.error('[WS Driver] Erro de conexão.');
  };
}

export function pararColeta() {
  // Enviar desconexão graciosa
  if (driverWs?.readyState === WebSocket.OPEN) {
    driverWs.send(JSON.stringify({ tipo: 'desconectar' }));
    setTimeout(() => {
      driverWs?.close();
      driverWs = null;
    }, 500);
  }

  _limparGPS();
  coletando = false;
}

function _limparGPS() {
  if (watchId !== null) {
    navigator.geolocation.clearWatch(watchId);
    watchId = null;
  }
}

// --- Filtro local por bairro ---
export function filtrarPorBairro(caminhoes: Map<string, CaminhaoPos>, bairro: string | null): CaminhaoPos[] {
  const arr = Array.from(caminhoes.values());
  if (!bairro) return arr;
  // Filtro simplificado — em produção, usaria o endereço geocodificado
  return arr.filter(c => c.endereco?.includes(bairro));
}
