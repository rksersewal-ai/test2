// =============================================================================
// FILE: frontend/public/sw.js
// SPRINT 8 — PWA Service Worker
//
// Strategy:
//   Static assets  → Cache-first (shell, CSS, JS)
//   API calls      → Network-first (LAN always available; fail fast)
//   /scanner       → Cache-first (works offline for capture step)
//   /s/{token}/    → Network-only (public share links must be fresh)
//
// Cache version: bump CACHE_VER on each release to invalidate old assets.
// =============================================================================

const CACHE_VER     = 'edms-v8';
const STATIC_CACHE  = `${CACHE_VER}-static`;
const API_CACHE     = `${CACHE_VER}-api`;

const PRECACHE_URLS = [
  '/',
  '/scanner',
  '/documents',
  '/offline.html',
  // Bundled JS/CSS injected by build tool at deploy time
];

// ---- Install: pre-cache shell ------------------------------------------
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

// ---- Activate: clean old caches ----------------------------------------
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== STATIC_CACHE && k !== API_CACHE)
            .map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// ---- Fetch: routing strategy -------------------------------------------
self.addEventListener('fetch', event => {
  const { request } = event;
  const url         = new URL(request.url);

  // Public share links: always network
  if (url.pathname.startsWith('/s/')) {
    event.respondWith(fetch(request));
    return;
  }

  // API calls: network-first, no cache fallback (LAN expected)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(() =>
        new Response(
          JSON.stringify({ error: 'Network unavailable. Check LAN connection.' }),
          { status: 503, headers: { 'Content-Type': 'application/json' } }
        )
      )
    );
    return;
  }

  // Static assets + scanner page: cache-first
  event.respondWith(
    caches.match(request).then(cached =>
      cached || fetch(request).then(response => {
        // Cache successful GET responses for static assets
        if (request.method === 'GET' && response.status === 200) {
          caches.open(STATIC_CACHE).then(c => c.put(request, response.clone()));
        }
        return response;
      }).catch(() =>
        caches.match('/offline.html')
      )
    )
  );
});
