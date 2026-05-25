/**
 * Cadê o Lixeiro? v2.0 — Push Notification Service
 *
 * Registra Service Worker, solicita permissão de notificação,
 * e gerencia subscriptions com o backend.
 * Ref: NOT-1 SDD §2.1
 */

const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Registra o Service Worker se suportado.
 */
export async function registrarServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (!('serviceWorker' in navigator)) {
    console.warn('[Push] Service Worker nao suportado.');
    return null;
  }

  try {
    const reg = await navigator.serviceWorker.register('/sw.js');
    console.log('[Push] Service Worker registrado.');
    return reg;
  } catch (err) {
    console.error('[Push] Erro ao registrar SW:', err);
    return null;
  }
}

/**
 * Solicita permissão de notificação ao usuário.
 */
export async function solicitarPermissao(): Promise<boolean> {
  if (!('Notification' in window)) {
    console.warn('[Push] Notifications nao suportadas.');
    return false;
  }

  if (Notification.permission === 'granted') return true;
  if (Notification.permission === 'denied') return false;

  const result = await Notification.requestPermission();
  return result === 'granted';
}

/**
 * Registra uma subscription de push para um bairro.
 */
export async function subscribePush(bairroId: string): Promise<{ id: string } | null> {
  try {
    // 1. Registrar SW
    const reg = await registrarServiceWorker();
    if (!reg) return null;

    // 2. Pedir permissão
    const permitido = await solicitarPermissao();
    if (!permitido) return null;

    // 3. Obter subscription
    // Nota: Em produção, usar VAPID_PUBLIC_KEY do .env
    // Para MVP, usamos subscription sem applicationServerKey
    let subscription = await reg.pushManager.getSubscription();

    if (!subscription) {
      subscription = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        // applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      });
    }

    const subJson = subscription.toJSON();

    // 4. Enviar para o backend
    const res = await fetch(`${API_URL}/api/notificacoes/subscribe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        bairro_id: bairroId,
        endpoint: subJson.endpoint,
        p256dh: subJson.keys?.p256dh || '',
        auth_key: subJson.keys?.auth || '',
      }),
    });

    if (res.ok) {
      const data = await res.json();
      console.log('[Push] Subscription registrada:', data.id);
      return data;
    }

    return null;
  } catch (err) {
    console.error('[Push] Erro ao subscribir:', err);
    return null;
  }
}

/**
 * Remove uma subscription de push.
 */
export async function unsubscribePush(subId: string): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/api/notificacoes/subscribe/${subId}`, {
      method: 'DELETE',
    });
    return res.ok;
  } catch {
    return false;
  }
}

/**
 * Verifica se há subscription ativa para um endpoint/bairro.
 */
export async function verificarSubscription(bairroId: string): Promise<{ subscribed: boolean; id?: string }> {
  try {
    const reg = await navigator.serviceWorker?.ready;
    const sub = await reg?.pushManager.getSubscription();
    if (!sub) return { subscribed: false };

    const res = await fetch(
      `${API_URL}/api/notificacoes/status?bairro_id=${bairroId}&endpoint=${encodeURIComponent(sub.endpoint)}`
    );
    if (res.ok) {
      return await res.json();
    }
    return { subscribed: false };
  } catch {
    return { subscribed: false };
  }
}
