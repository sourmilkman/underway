// Offline helper for the web version of Underway.
// The saved copy is always used first, so the app opens instantly with no signal or a weak one.
// When there is a connection, a fresh copy is fetched quietly in the background for next time.
const VER = 'underway-__VER__';
const CORE = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './pdf.min.js', './pdf.worker.min.js'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VER).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== VER).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Fetch with a time limit, so a connection that never answers can't hold anything up.
const fetchWithin = (req, ms) => new Promise((resolve, reject) => {
  const t = setTimeout(() => reject(new Error('timeout')), ms);
  fetch(req).then(r => { clearTimeout(t); resolve(r); }, err => { clearTimeout(t); reject(err); });
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return; // the app uses nothing from other sites

  if (req.mode === 'navigate') {
    e.respondWith(caches.open(VER).then(async c => {
      const saved = await c.match('./index.html');
      const refresh = fetchWithin(req, 8000).then(r => { if (r.ok) c.put('./index.html', r.clone()); return r; });
      if (saved) { e.waitUntil(refresh.catch(() => {})); return saved; }
      return refresh;
    }));
    return;
  }

  e.respondWith(caches.match(req, { ignoreSearch: true }).then(hit => hit || fetchWithin(req, 8000).then(r => {
    if (r.ok) { const cp = r.clone(); caches.open(VER).then(c => c.put(req, cp)); }
    return r;
  })));
});
