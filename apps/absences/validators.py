import os

from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png")
MAX_SIZE_BYTES = 5 * 1024 * 1024


def validate_justification_file(file):
    """CDC §12.1.2 : PDF/JPG/PNG, max 5 Mo. Validation par extension — moins
    strict que le traitement de la photo de pointage (re-encodage par Pillow)
    car ce champ accepte aussi des PDF, non ré-encodables de la même façon ;
    enjeu de sécurité moindre qu'une preuve biométrique de présence."""
    if file.size > MAX_SIZE_BYTES:
        raise ValidationError("Fichier trop volumineux (max 5 Mo).")
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError("Format non autorisé (PDF, JPG ou PNG uniquement).")
