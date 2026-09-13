/* Service Worker — CDC §4.4/§9.7/§23.1. JS vanilla, pas de framework (CDC §24.1).
 *
 * Stratégie : "app shell + pages visitées" — chaque page GET visitée avec
 * succès est mise en cache opportunément ; en cas de perte réseau, la
 * dernière version connue est resservie. Aucune requête POST n'est
 * interceptée (le pointage POST passe toujours par le réseau ou par la file
 * d'attente IndexedDB gérée dans clock.js, jamais par ce cache HTTP).
 */
const CACHE_NAME = "geopresence-shell-v15";
const OFFLINE_FALLBACK_URL = "/static/offline.html";
// Au-delà de ce délai, on cesse d'attendre le réseau pour une navigation et
// on ressert la dernière version connue de la page (ou la page hors ligne) —
// évite l'écran blanc figé "au clic" sur une connexion lente/instable, sans
// pour autant renoncer à la fraîcheur quand le réseau répond normalement.
const NAV_NETWORK_TIMEOUT_MS = 3500;
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
    const network = fetch(request)
      .then((response) => cachePut(request, response))
      .catch(() => null);
    const timeout = new Promise((resolve) => setTimeout(() => resolve(null), NAV_NETWORK_TIMEOUT_MS));
    event.respondWith(
      Promise.race([network, timeout]).then(
        (response) =>
          response ||
          caches
            .match(request)
            .then((cached) => cached || network) // pas de cache : on laisse le réseau finir malgré tout
            .then((r) => r || caches.match(OFFLINE_FALLBACK_URL))
      )
    );
    return;
  }

  event.respondWith(
    caches.match(request).then((cached) => cached || fetch(request).then((response) => cachePut(request, response)))
  );
});
