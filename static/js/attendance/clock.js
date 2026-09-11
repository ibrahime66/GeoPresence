/* Pointage — CDC §9.3 + §9.7 (mode hors ligne). JS vanilla, pas de framework (CDC §24.1).
 * Carte GPS interactive en lecture seule (pas de photo) : le marqueur suit la
 * position réelle de l'appareil (watchPosition), il n'est jamais déplaçable —
 * l'intérêt anti-fraude du pointage GPS dépend de ce que la position vienne
 * bien du capteur, pas d'un clic sur la carte. */
(() => {
  "use strict";

  const config = JSON.parse(document.getElementById("clock-config").textContent);
  // Zones GPS émises séparément via {{ ...|json_script }} (audit sécurité §8) —
  // échappement sûr des libellés de zone dans le <script>.
  const zonesEl = document.getElementById("clock-zones");
  config.zones = zonesEl ? JSON.parse(zonesEl.textContent) : [];

  // Icônes hébergées localement plutôt que sur cdn.jsdelivr.net : la
  // Content-Security-Policy (img-src) n'autorise que 'self'/data:/tuiles
  // OpenStreetMap, un CDN d'icônes supplémentaire n'apporterait rien.
  // L.Icon.Default préfixe toujours iconUrl/shadowUrl par `imagePath` (auto-
  // détecté depuis l'URL du CSS Leaflet, ici cdn.jsdelivr.net) — il faut donc
  // remplacer imagePath lui-même, pas seulement les noms de fichiers.
  if (typeof L !== "undefined") {
    L.Icon.Default.imagePath = "/static/img/leaflet/";
  }

  const DB_NAME = "geopresence-offline";
  const STORE_NAME = "pending_clocks";

  const els = {
    idle: document.getElementById("clock-idle"),
    startBtn: document.getElementById("btn-start-clock"),
    status: document.getElementById("clock-status"),
    statusText: document.getElementById("clock-status-text"),
    mapWrap: document.getElementById("clock-map-wrap"),
    map: document.getElementById("clock-map"),
    accuracyText: document.getElementById("clock-accuracy-text"),
    recenterBtn: document.getElementById("btn-recenter"),
    cancelBtn: document.getElementById("btn-cancel"),
    confirmBtn: document.getElementById("btn-confirm"),
    result: document.getElementById("clock-result"),
    offlineBadge: document.getElementById("clock-offline-badge"),
  };

  let watchId = null;
  let gpsData = null;
  let leafletMap = null;
  let marker = null;
  let accuracyCircle = null;

  function show(el) {
    el.hidden = false;
  }
  function hide(el) {
    el.hidden = true;
  }
  function setStatusText(text) {
    els.statusText.textContent = text;
  }
  function showResult(kind, message) {
    els.result.innerHTML = `<div class="alert alert-${kind}">${message}</div>`;
  }

  function stopWatch() {
    if (watchId !== null) {
      navigator.geolocation.clearWatch(watchId);
      watchId = null;
    }
  }

  function resetToIdle() {
    stopWatch();
    hide(els.status);
    hide(els.mapWrap);
    show(els.idle);
    gpsData = null;
  }

  // ---------- File d'attente hors ligne (IndexedDB) — CDC §9.7.2/§9.7.3 ----------
  // Les pointages mis en attente ne sont pas chiffrés dans IndexedDB (CDC
  // §9.7.4 recommande un chiffrement lié à la session) : simplification
  // assumée — voir la documentation du projet pour ce compromis.

  function openDb() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, 1);
      req.onupgradeneeded = () => {
        req.result.createObjectStore(STORE_NAME, { keyPath: "id", autoIncrement: true });
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async function queueOffline(payload) {
    const db = await openDb();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      tx.objectStore(STORE_NAME).add(payload);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }

  async function getQueuedClocks() {
    const db = await openDb();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readonly");
      const req = tx.objectStore(STORE_NAME).getAll();
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async function removeQueued(id) {
    const db = await openDb();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      tx.objectStore(STORE_NAME).delete(id);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }

  async function updatePendingBadge() {
    if (!els.offlineBadge) return;
    let pending = [];
    try {
      pending = await getQueuedClocks();
    } catch (e) {
      return;
    }
    if (pending.length === 0) {
      els.offlineBadge.hidden = true;
      els.offlineBadge.innerHTML = "";
      return;
    }
    els.offlineBadge.hidden = false;
    const label = pending.length === 1 ? "1 pointage" : `${pending.length} pointages`;
    els.offlineBadge.innerHTML =
      `<div class="alert alert-warning mb-3">${label} en attente de synchronisation (hors ligne).</div>`;
  }

  function sendClock(payload, mode) {
    const formData = new FormData();
    formData.append("clock_type", payload.clockType);
    formData.append("latitude", payload.latitude);
    formData.append("longitude", payload.longitude);
    formData.append("gps_accuracy", payload.accuracy);
    formData.append("is_gps_mocked", payload.isMocked ? "true" : "false");
    formData.append("client_time", payload.clientTime);
    if (mode) formData.append("mode", mode);
    // RM-QR-001 : uniquement informatif (l'agence a déjà été pré-sélectionnée
    // côté serveur, la vérification GPS ci-dessus est inchangée) — trace dans
    // l'historique que ce pointage vient d'un scan plutôt que du bouton.
    if (config.source) formData.append("source", config.source);

    return fetch(config.apiUrl, {
      method: "POST",
      headers: { "X-CSRFToken": config.csrfToken },
      body: formData,
      credentials: "same-origin",
    }).then(async (response) => {
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Erreur lors de l'enregistrement du pointage.");
      }
      return data;
    });
  }

  async function syncPendingClocks() {
    if (!navigator.onLine) return;
    let pending;
    try {
      pending = await getQueuedClocks();
    } catch (e) {
      return;
    }
    for (const item of pending) {
      try {
        await sendClock(item, "OFFLINE");
        await removeQueued(item.id);
      } catch (error) {
        // Réseau toujours indisponible, ou erreur serveur — on réessaiera au
        // prochain événement "online" plutôt que de perdre la file.
        break;
      }
    }
    await updatePendingBadge();
  }

  if (!els.startBtn) {
    // Journée terminée — aucun bouton à câbler, mais la synchro/le badge restent utiles.
    updatePendingBadge();
    window.addEventListener("online", syncPendingClocks);
    return;
  }

  els.startBtn.addEventListener("click", startClockFlow);
  els.cancelBtn.addEventListener("click", resetToIdle);
  els.confirmBtn.addEventListener("click", submitClock);
  if (els.recenterBtn) els.recenterBtn.addEventListener("click", recenterMap);

  updatePendingBadge();
  syncPendingClocks();
  window.addEventListener("online", syncPendingClocks);

  function startClockFlow() {
    els.result.innerHTML = "";
    hide(els.idle);
    show(els.status);
    setStatusText("Acquisition de la position GPS…");
    acquireGeolocation();
  }

  function acquireGeolocation() {
    if (!("geolocation" in navigator)) {
      showResult("danger", "Votre navigateur ne supporte pas la géolocalisation. Pointage impossible.");
      resetToIdle();
      return;
    }
    navigator.geolocation.getCurrentPosition(onFirstFix, onGeolocationError, {
      enableHighAccuracy: true,
      timeout: 15000,
      maximumAge: 0,
    });
  }

  function onFirstFix(position) {
    updateGpsData(position);
    hide(els.status);
    show(els.mapWrap);
    initMap(gpsData.latitude, gpsData.longitude, gpsData.accuracy);
    // Position suivie en direct pendant que la carte est affichée — la
    // dernière valeur reçue est celle envoyée au clic sur "Pointer ici".
    watchId = navigator.geolocation.watchPosition(onWatchUpdate, () => {}, {
      enableHighAccuracy: true,
      maximumAge: 2000,
    });
  }

  function updateGpsData(position) {
    gpsData = {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      accuracy: position.coords.accuracy,
      // Non standard / support navigateur très limité : meilleur effort pour
      // signaler une position simulée (CDC §8.6) quand l'information existe.
      isMocked: Boolean(position.coords.mocked || position.mocked),
    };
  }

  function onWatchUpdate(position) {
    updateGpsData(position);
    if (marker) {
      const latLng = [gpsData.latitude, gpsData.longitude];
      marker.setLatLng(latLng);
      accuracyCircle.setLatLng(latLng);
      accuracyCircle.setRadius(gpsData.accuracy || 0);
      els.accuracyText.textContent = `Précision : ±${Math.round(gpsData.accuracy || 0)} m`;
    }
  }

  function onGeolocationError(error) {
    const messages = {
      1: "Permission de géolocalisation refusée. Activez-la pour pouvoir pointer.",
      2: "Position GPS indisponible. Réessayez en étant à l'extérieur ou près d'une fenêtre.",
      3: "Délai d'acquisition GPS dépassé. Réessayez.",
    };
    showResult("danger", messages[error.code] || "Erreur de géolocalisation.");
    resetToIdle();
  }

  function recenterMap() {
    if (!leafletMap || !gpsData) return;
    leafletMap.setView([gpsData.latitude, gpsData.longitude], 17);
  }

  function initMap(lat, lon, accuracy) {
    if (typeof L === "undefined") return;
    if (leafletMap) {
      leafletMap.remove();
      leafletMap = null;
    }
    const latLng = [lat, lon];
    leafletMap = L.map(els.map, { zoomControl: true, dragging: true, scrollWheelZoom: false }).setView(latLng, 17);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; contributeurs OpenStreetMap",
    }).addTo(leafletMap);

    // Zone(s) de pointage autorisée(s) de l'agence — affichées à titre
    // indicatif pour que l'employé voie s'il est dans le périmètre, sans
    // pouvoir les déplacer (lecture seule).
    const zones = config.zones || [];
    const zoneBounds = [];
    zones.forEach((zone) => {
      const zoneLatLng = [zone.latitude, zone.longitude];
      L.circle(zoneLatLng, {
        radius: zone.radius,
        color: "#16a34a",
        fillColor: "#16a34a",
        fillOpacity: 0.08,
        weight: 1.5,
        dashArray: "6 4",
      })
        .addTo(leafletMap)
        .bindTooltip(zone.label, { permanent: false });
      zoneBounds.push(zoneLatLng);
    });

    // Pas d'option "draggable" : le marqueur reflète uniquement la position
    // GPS réelle de l'appareil, jamais un point choisi manuellement.
    marker = L.marker(latLng).addTo(leafletMap);
    accuracyCircle = L.circle(latLng, {
      radius: accuracy || 0,
      color: "#0B63F6",
      fillColor: "#0B63F6",
      fillOpacity: 0.12,
      weight: 1.5,
    }).addTo(leafletMap);
    els.accuracyText.textContent = `Précision : ±${Math.round(accuracy || 0)} m`;

    if (zoneBounds.length) {
      leafletMap.fitBounds([latLng, ...zoneBounds], { padding: [30, 30], maxZoom: 18 });
    }

    setTimeout(() => leafletMap.invalidateSize(), 100);
  }

  function submitClock() {
    if (!gpsData) return;
    els.confirmBtn.disabled = true;
    els.confirmBtn.textContent = "Envoi en cours…";
    stopWatch();

    const payload = {
      clockType: config.nextClockType,
      // navigator.geolocation renvoie des nombres à pleine précision flottante
      // (souvent 15+ chiffres, ex. 9.680608712345678) : envoyés tels quels, ils
      // dépassent le max_digits=10 du DecimalField serveur (ClockForm) et le
      // pointage est rejeté avec une erreur générique — arrondi ici à une
      // précision largement suffisante (7 décimales ≈ 1 cm pour lat/lon,
      // 2 décimales pour une précision GPS exprimée en mètres).
      latitude: gpsData.latitude.toFixed(7),
      longitude: gpsData.longitude.toFixed(7),
      accuracy: gpsData.accuracy != null ? gpsData.accuracy.toFixed(2) : gpsData.accuracy,
      isMocked: gpsData.isMocked,
      clientTime: new Date().toISOString(),
    };

    sendClock(payload)
      .then((data) => {
        let message = `${data.status_display}, enregistré à ${new Date(data.server_time).toLocaleTimeString()} (${data.agency}).`;
        if (data.late_minutes) message += ` Retard : ${data.late_minutes} min.`;
        if (data.early_leave_minutes) message += ` Départ anticipé : ${data.early_leave_minutes} min.`;
        if (data.overtime_minutes) message += ` Heures sup. : ${data.overtime_minutes} min.`;
        showResult("success", message);
        hide(els.mapWrap);
        setTimeout(() => window.location.reload(), 2000);
      })
      .catch(async (error) => {
        if (error instanceof TypeError) {
          // fetch() ne rejette avec un TypeError que lorsque le réseau est
          // injoignable (contrairement à une réponse HTTP d'erreur, qui est
          // un rejet applicatif normal) — CDC §9.7.2 : file d'attente hors ligne.
          try {
            await queueOffline(payload);
            showResult(
              "warning",
              "Hors ligne : pointage enregistré sur cet appareil, il sera envoyé automatiquement au retour du réseau."
            );
            hide(els.mapWrap);
            await updatePendingBadge();
            setTimeout(resetToIdle, 2500);
          } catch (dbError) {
            showResult("danger", "Impossible d'enregistrer le pointage hors ligne sur cet appareil.");
            els.confirmBtn.disabled = false;
            els.confirmBtn.textContent = "Pointer ici";
          }
          return;
        }
        showResult("danger", error.message);
        els.confirmBtn.disabled = false;
        els.confirmBtn.textContent = "Pointer ici";
      });
  }
})();
