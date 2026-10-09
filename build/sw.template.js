// Offline cache for Underway. App files are cached on install; fonts and the PDF viewer are cached the first time they load.
const VER = 'underway-__VER__';
const CORE = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './pdf.min.js', './pdf.worker.min.js'];
self.addEventListener('install', e => { e.waitUntil(caches.open(VER).then(c => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VER).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const extra = /fonts\.(googleapis|gstatic)\.com|cdnjs\.cloudflare\.com/.test(url.host);
  if (url.origin === location.origin && req.mode === 'navigate') {
    // network first for the page so updates arrive, cache when offline
    e.respondWith(fetch(req).then(r => { const cp = r.clone(); caches.open(VER).then(c => c.put('./index.html', cp)); return r; }).catch(() => caches.match('./index.html')));
    return;
  }
  if (url.origin === location.origin || extra) {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => { if (r.ok || r.type === 'opaque') { const cp = r.clone(); caches.open(VER).then(c => c.put(req, cp)); } return r; })));
  }
});
