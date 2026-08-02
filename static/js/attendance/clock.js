/* Pointage — CDC §9.3. JS vanilla, pas de framework (contrainte CDC §24.1). */
(() => {
  "use strict";

  const config = JSON.parse(document.getElementById("clock-config").textContent);
  const COUNTDOWN_SECONDS = 3;

  const els = {
    idle: document.getElementById("clock-idle"),
    startBtn: document.getElementById("btn-start-clock"),
    status: document.getElementById("clock-status"),
    statusText: document.getElementById("clock-status-text"),
    camera: document.getElementById("clock-camera"),
    video: document.getElementById("clock-video"),
    countdown: document.getElementById("clock-countdown"),
    preview: document.getElementById("clock-preview"),
    photoPreview: document.getElementById("clock-photo-preview"),
    retakeBtn: document.getElementById("btn-retake"),
    confirmBtn: document.getElementById("btn-confirm"),
    result: document.getElementById("clock-result"),
    canvas: document.getElementById("clock-canvas"),
  };

  let mediaStream = null;
  let capturedBlob = null;
  let gpsData = null;

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

  function resetToIdle() {
    if (mediaStream) {
      mediaStream.getTracks().forEach((t) => t.stop());
      mediaStream = null;
    }
    hide(els.status);
    hide(els.camera);
    hide(els.preview);
    show(els.idle);
    capturedBlob = null;
    gpsData = null;
  }

  if (!els.startBtn) {
    // Journée terminée — aucun bouton à câbler.
    return;
  }

  els.startBtn.addEventListener("click", startClockFlow);
  els.retakeBtn.addEventListener("click", () => {
    hide(els.preview);
    startCamera();
  });
  els.confirmBtn.addEventListener("click", submitClock);

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
    navigator.geolocation.getCurrentPosition(onGeolocationSuccess, onGeolocationError, {
      enableHighAccuracy: true,
      timeout: 15000,
      maximumAge: 0,
    });
  }

  function onGeolocationSuccess(position) {
    gpsData = {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      accuracy: position.coords.accuracy,
      // Non standard / support navigateur très limité : meilleur effort pour
      // signaler une position simulée (CDC §8.6) quand l'information existe.
      isMocked: Boolean(position.coords.mocked || position.mocked),
    };
    startCamera();
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

  function startCamera() {
    setStatusText("Activation de la caméra…");
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 } } })
      .then((stream) => {
        mediaStream = stream;
        els.video.srcObject = stream;
        hide(els.status);
        show(els.camera);
        runCountdown();
      })
      .catch(() => {
        showResult("danger", "Impossible d'accéder à la caméra. Vérifiez les permissions.");
        resetToIdle();
      });
  }

  function runCountdown() {
    let remaining = COUNTDOWN_SECONDS;
    els.countdown.textContent = remaining;
    const interval = setInterval(() => {
      remaining -= 1;
      if (remaining <= 0) {
        clearInterval(interval);
        capturePhoto();
      } else {
        els.countdown.textContent = remaining;
      }
    }, 1000);
  }

  function capturePhoto() {
    const canvas = els.canvas;
    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext("2d");
    // Effet miroir, cohérent avec l'aperçu selfie affiché à l'écran.
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(els.video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        capturedBlob = blob;
        els.photoPreview.src = URL.createObjectURL(blob);
        if (mediaStream) {
          mediaStream.getTracks().forEach((t) => t.stop());
          mediaStream = null;
        }
        hide(els.camera);
        show(els.preview);
      },
      "image/jpeg",
      0.85
    );
  }

  function submitClock() {
    els.confirmBtn.disabled = true;
    els.confirmBtn.textContent = "Envoi en cours…";

    const formData = new FormData();
    formData.append("clock_type", config.nextClockType);
    formData.append("latitude", gpsData.latitude);
    formData.append("longitude", gpsData.longitude);
    formData.append("gps_accuracy", gpsData.accuracy);
    formData.append("is_gps_mocked", gpsData.isMocked ? "true" : "false");
    formData.append("client_time", new Date().toISOString());
    formData.append("photo", capturedBlob, "clock.jpg");

    fetch(config.apiUrl, {
      method: "POST",
      headers: { "X-CSRFToken": config.csrfToken },
      body: formData,
      credentials: "same-origin",
    })
      .then(async (response) => {
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "Erreur lors de l'enregistrement du pointage.");
        }
        return data;
      })
      .then((data) => {
        let message = `${data.status_display} — enregistré à ${new Date(data.server_time).toLocaleTimeString()} (${data.agency}).`;
        if (data.late_minutes) message += ` Retard : ${data.late_minutes} min.`;
        if (data.early_leave_minutes) message += ` Départ anticipé : ${data.early_leave_minutes} min.`;
        if (data.overtime_minutes) message += ` Heures sup. : ${data.overtime_minutes} min.`;
        showResult("success", message);
        hide(els.preview);
        setTimeout(() => window.location.reload(), 2000);
      })
      .catch((error) => {
        showResult("danger", error.message);
        els.confirmBtn.disabled = false;
        els.confirmBtn.textContent = "Confirmer le pointage";
      });
  }
})();
