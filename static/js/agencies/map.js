/* Carte interactive de saisie des coordonnées d'agence — CDC §7.4. JS vanilla + Leaflet. */
(() => {
  "use strict";

  const mapEl = document.getElementById("agency-map");
  if (!mapEl || typeof L === "undefined") return;

  const latInput = document.getElementById("id_latitude");
  const lonInput = document.getElementById("id_longitude");
  const radiusInput = document.getElementById("id_radius_meters");
  const searchInput = document.getElementById("agency-address-search");
  const searchBtn = document.getElementById("agency-address-search-btn");

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
    const pos = marker.getLatLng();
    setPosition(pos.lat, pos.lng);
  });

  map.on("click", (e) => {
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

  // Une carte Leaflet initialisée dans un conteneur encore invisible (onglet,
  // accordéon...) se rend mal tant qu'aucun redimensionnement n'est déclenché —
  // pas le cas ici (carte toujours visible), mais gratuit à sécuriser.
  setTimeout(() => map.invalidateSize(), 100);
})();
