/* Carte interactive de saisie des coordonnées d'agence — CDC §7.4. JS vanilla + Leaflet. */
(() => {
  "use strict";

  const mapEl = document.getElementById("agency-map");
  if (!mapEl || typeof L === "undefined") return;

  // Icônes hébergées localement plutôt que sur cdn.jsdelivr.net : la
  // Content-Security-Policy (img-src) n'autorise que 'self'/data:/tuiles
  // OpenStreetMap, un CDN d'icônes supplémentaire n'apporterait rien.
  // L.Icon.Default préfixe toujours iconUrl/shadowUrl par `imagePath` (auto-
  // détecté depuis l'URL du CSS Leaflet, ici cdn.jsdelivr.net) — il faut donc
  // remplacer imagePath lui-même, pas seulement les noms de fichiers.
  L.Icon.Default.imagePath = "/static/img/leaflet/";

  const latInput = document.getElementById("id_latitude");
  const lonInput = document.getElementById("id_longitude");
  const radiusInput = document.getElementById("id_radius_meters");
  const searchInput = document.getElementById("agency-address-search");
  const searchBtn = document.getElementById("agency-address-search-btn");
  const locateBtn = document.getElementById("agency-locate-btn");
  const locateStatus = document.getElementById("agency-locate-status");

  const DEFAULT_CENTER = [48.8566, 2.3522]; // Paris — utilisé seulement si aucune coordonnée existante.
  const hasExisting = latInput.value && lonInput.value;
  const initialCenter = hasExisting ? [parseFloat(latInput.value), parseFloat(lonInput.value)] : DEFAULT_CENTER;
  const initialRadius = parseFloat(radiusInput.value) || 200;

  const map = L.map(mapEl).setView(initialCenter, hasExisting ? 16 : 12);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; contributeurs OpenStreetMap",
  }).addTo(map);

  const marker = L.marker(initialCenter, { draggable: true }).addTo(map);
  const circle = L.circle(initialCenter, {
    radius: initialRadius,
    color: "#0B63F6",
    fillColor: "#0B63F6",
    fillOpacity: 0.12,
    weight: 1.5,
  }).addTo(map);

  function setPosition(lat, lon) {
    const latLng = [lat, lon];
    marker.setLatLng(latLng);
    circle.setLatLng(latLng);
    latInput.value = lat.toFixed(7);
    lonInput.value = lon.toFixed(7);
  }

  marker.on("dragend", () => {
    stopFollowing();
    const pos = marker.getLatLng();
    setPosition(pos.lat, pos.lng);
  });

  map.on("click", (e) => {
    stopFollowing();
    setPosition(e.latlng.lat, e.latlng.lng);
  });

  radiusInput.addEventListener("input", () => {
    const value = parseFloat(radiusInput.value);
    if (!isNaN(value) && value > 0) {
      circle.setRadius(value);
    }
  });

  function searchAddress() {
    const query = searchInput.value.trim();
    if (!query) return;
    searchBtn.disabled = true;
    searchBtn.textContent = "Recherche…";

    fetch(`https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(query)}`)
      .then((response) => response.json())
      .then((results) => {
        if (!results.length) {
          alert("Aucune adresse trouvée.");
          return;
        }
        const { lat, lon } = results[0];
        const latNum = parseFloat(lat);
        const lonNum = parseFloat(lon);
        setPosition(latNum, lonNum);
        map.setView([latNum, lonNum], 16);
      })
      .catch(() => {
        alert("Erreur lors de la recherche d'adresse — réessayez.");
      })
      .finally(() => {
        searchBtn.disabled = false;
        searchBtn.textContent = "Rechercher";
      });
  }

  searchBtn.addEventListener("click", searchAddress);
  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      searchAddress();
    }
  });

  // "Ma position" suit la position GPS réelle de l'admin EN CONTINU (comme le
  // pointage employé) — utile quand l'admin se déplace physiquement jusqu'à
  // l'agence pour pointer l'endroit exact avec son téléphone. Le suivi
  // s'arrête dès que l'admin ajuste la position à la main (glisser le
  // marqueur ou cliquer ailleurs sur la carte), pour lui laisser la main.
  const locateBtnOriginalHTML = locateBtn.innerHTML;
  let watchId = null;

  // Le statut s'affiche sur la page plutôt que via alert() : une alert() peut
  // être coupée sans bruit par certains réglages navigateur ("ne plus afficher
  // les messages de ce site"), ce qui donnerait l'impression d'un clic sans
  // aucun effet alors qu'une erreur s'est bien produite.
  function setStatus(text, isError) {
    locateStatus.textContent = text;
    locateStatus.className = isError ? "small mb-3 text-danger" : "small mb-3 text-muted";
  }

  const GEOLOCATION_ERROR_MESSAGES = {
    1: "Permission de géolocalisation refusée par le navigateur.",
    2: "Position indisponible — vérifiez que la localisation est activée sur cet ordinateur.",
    3: "Délai dépassé en attendant une position GPS.",
  };

  function stopFollowing() {
    if (watchId === null) return;
    navigator.geolocation.clearWatch(watchId);
    watchId = null;
    locateBtn.classList.remove("btn-primary");
    locateBtn.classList.add("btn-outline-secondary");
    locateBtn.innerHTML = locateBtnOriginalHTML;
  }

  function useMyLocation() {
    if (watchId !== null) {
      stopFollowing();
      setStatus("Suivi arrêté.", false);
      return;
    }
    if (!("geolocation" in navigator)) {
      setStatus("Ce navigateur ne supporte pas la géolocalisation.", true);
      return;
    }
    setStatus("Localisation en cours…", false);
    locateBtn.classList.remove("btn-outline-secondary");
    locateBtn.classList.add("btn-primary");
    locateBtn.textContent = "Suivi en direct… (cliquer pour arrêter)";
    let firstFix = true;
    watchId = navigator.geolocation.watchPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setPosition(latitude, longitude);
        map.setView([latitude, longitude], firstFix ? 17 : map.getZoom());
        setStatus(`Position reçue (précision ±${Math.round(position.coords.accuracy || 0)} m).`, false);
        firstFix = false;
      },
      (error) => {
        setStatus(GEOLOCATION_ERROR_MESSAGES[error.code] || `Erreur de géolocalisation (code ${error.code}).`, true);
        stopFollowing();
      },
      { enableHighAccuracy: true, maximumAge: 2000, timeout: 10000 }
    );
  }

  locateBtn.addEventListener("click", useMyLocation);

  // Une carte Leaflet initialisée dans un conteneur encore invisible (onglet,
  // accordéon...) se rend mal tant qu'aucun redimensionnement n'est déclenché —
  // pas le cas ici (carte toujours visible), mais gratuit à sécuriser.
  setTimeout(() => map.invalidateSize(), 100);
})();
