import os
import uuid


def generate_upload_filename(filename):
    """CDC §13.3.7 : renommage systématique des fichiers uploadés avec un UUID —
    on ne fait jamais confiance au nom fourni par le client (conflits, longueur
    non bornée, tentative d'attaque via le nom de fichier)."""
    ext = os.path.splitext(filename)[1].lower()
    return f"{uuid.uuid4()}{ext}"
