/* Service Worker — CDC §4.4/§9.7/§23.1. JS vanilla, pas de framework (CDC §24.1).
 *
 * Stratégie : "app shell + pages visitées" — chaque page GET visitée avec
 * succès est mise en cache opportunément ; en cas de perte réseau, la
 * dernière version connue est resservie. Aucune requête POST n'est
 * interceptée (le pointage POST passe toujours par le réseau ou par la file
 * d'attente IndexedDB gérée dans clock.js, jamais par ce cache HTTP).
 */
const CACHE_NAME = "geopresence-shell-v3";
const OFFLINE_FALLBACK_URL = "/static/offline.html";
const SHELL_ASSETS = [
  "/static/css/main.css",
  "/static/img/logo-mark.png",
  "/static/img/favicon-192.png",
  OFFLINE_FALLBACK_URL,
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

function cachePut(request, response) {
  const copy = response.clone();
  caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
  return response;
}

self.addEventListener("fetch", (event) => {
  const { request } = event;

  // Seules les requêtes de lecture (GET) passent par le cache — un pointage
  // (POST) hors ligne est de la responsabilité de la file IndexedDB, pas de
  // ce cache HTTP générique (CDC §9.7.2).
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => cachePut(request, response))
        .catch(() => caches.match(request).then((cached) => cached || caches.match(OFFLINE_FALLBACK_URL)))
    );
    return;
  }

  event.respondWith(
    caches.match(request).then((cached) => cached || fetch(request).then((response) => cachePut(request, response)))
  );
});
