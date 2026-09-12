"""RM-QR-001 : génération du QR de pointage imprimable d'une agence."""

import base64
from io import BytesIO

import qrcode
from qrcode.constants import ERROR_CORRECT_Q


def qr_scan_url(request, agency):
    """URL absolue encodée dans le QR imprimable. Contient le jeton
    régénérable de l'agence (cf. Agency.qr_token), pas seulement son UUID —
    voir le commentaire du champ pour le modèle de sécurité complet."""
    from django.urls import reverse

    path = reverse("attendance:qr_entry", args=[agency.id, agency.qr_token])
    return request.build_absolute_uri(path)


def qr_code_data_uri(data):
    """PNG encodé en base64, directement utilisable dans un <img src="...">
    — évite d'exposer une route d'image séparée (donc une nouvelle surface à
    sécuriser) pour un simple encart imprimable. Correction d'erreur "Q"
    (~25%) plutôt que le défaut "M" : le code est imprimé et affiché en
    continu sur site, donc exposé à l'usure et aux taches."""
    img = qrcode.make(data, error_correction=ERROR_CORRECT_Q, box_size=10, border=2)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
