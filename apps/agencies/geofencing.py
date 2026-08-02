import math

# CDC §8.2 : formule de Haversine, R = 6371 km.
EARTH_RADIUS_METERS = 6_371_000

# CDC §8.4 : marge de tolérance ajoutée au rayon configuré, pour absorber
# l'imprécision GPS des smartphones (par défaut 30 m).
GPS_TOLERANCE_METERS = 30


def haversine_distance_meters(lat1, lon1, lat2, lon2):
    """Distance en mètres entre deux points GPS (formule de Haversine)."""
    phi1, phi2 = math.radians(float(lat1)), math.radians(float(lat2))
    delta_phi = math.radians(float(lat2) - float(lat1))
    delta_lambda = math.radians(float(lon2) - float(lon1))

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_METERS * math.asin(min(1, math.sqrt(a)))


def effective_radius_meters(base_radius, gps_accuracy=None):
    """Rayon effectif = rayon configuré + marge de tolérance (CDC §8.4).
    Si la précision GPS fournie par le navigateur dépasse déjà la marge par
    défaut, on l'ajoute intégralement plutôt que de refuser injustement un
    pointage pris avec un GPS peu précis (l'anomalie est de toute façon
    enregistrée séparément, cf. flag 'précision faible')."""
    tolerance = GPS_TOLERANCE_METERS
    if gps_accuracy and gps_accuracy > GPS_TOLERANCE_METERS:
        tolerance += float(gps_accuracy) - GPS_TOLERANCE_METERS
    return float(base_radius) + tolerance


def check_point_in_zone(lat, lon, zone_lat, zone_lon, zone_radius, gps_accuracy=None):
    """Retourne (autorisé: bool, distance_m: float, rayon_effectif_m: float)."""
    distance = haversine_distance_meters(lat, lon, zone_lat, zone_lon)
    radius = effective_radius_meters(zone_radius, gps_accuracy)
    return distance <= radius, distance, radius
