/**
 * Cadê o Lixeiro? v2.0 — Service Worker para Web Push
 * Ref: NOT-1 SDD §2.1
 */

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('push', (event) => {
  if (!event.data) return;

  let data;
  try {
    data = event.data.json();
  } catch {
    data = {
      title: 'Cade o Lixeiro?',
      body: event.data.text(),
    };
  }

  const options = {
    body: data.body || 'Notificacao recebida',
    icon: data.icon || '/favicon.png',
    badge: '/favicon.png',
    tag: data.tag || 'cade-o-lixeiro',
    vibrate: [200, 100, 200],
    data: {
      url: data.url || '/',
    },
  };

  event.waitUntil(
    self.registration.showNotification(
      data.title || 'Cade o Lixeiro?',
      options
    )
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = event.notification.data?.url || '/';

  event.waitUntil(
    self.clients.matchAll({ type: 'window' }).then((clients) => {
      // Se já tem uma janela aberta, foca nela
      for (const client of clients) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          return client.focus();
        }
      }
      // Senão, abre nova
      return self.clients.openWindow(url);
    })
  );
});
