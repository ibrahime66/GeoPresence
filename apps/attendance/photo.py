import io

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, UnidentifiedImageError

from . import constants


class InvalidPhotoError(Exception):
    pass


def process_photo(uploaded_file):
    """CDC §9.3.4 / RM-POINT-001 : la photo est obligatoire et re-traitée
    côté serveur — on ne fait jamais confiance au client, même si celui-ci a
    déjà capturé en JPEG 640x480 qualité 0.85 (défense en profondeur).

    Validation par contenu réel du fichier (PIL parse les octets, pas
    l'extension) plutôt que par une bibliothèque système supplémentaire type
    python-magic — cf. mémoire projet sur les conflits de paquets système déjà
    rencontrés sur cette machine."""
    if uploaded_file is None:
        raise InvalidPhotoError("Photo manquante — le pointage nécessite une photo (CDC §9.6).")
    if uploaded_file.size > constants.PHOTO_MAX_UPLOAD_SIZE_BYTES:
        raise InvalidPhotoError("Photo trop volumineuse (max 5 Mo).")

    try:
        image = Image.open(uploaded_file)
        image.verify()
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        image_format = image.format
    except (UnidentifiedImageError, OSError):
        raise InvalidPhotoError("Fichier image invalide ou corrompu.")

    if image_format not in ("JPEG", "PNG"):
        raise InvalidPhotoError("Format d'image non autorisé (JPEG ou PNG uniquement).")

    image = image.convert("RGB")
    image.thumbnail((constants.PHOTO_MAX_WIDTH, constants.PHOTO_MAX_HEIGHT), Image.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=constants.PHOTO_JPEG_QUALITY, optimize=True)
    size = buffer.getbuffer().nbytes
    buffer.seek(0)

    return InMemoryUploadedFile(buffer, None, "clock.jpg", "image/jpeg", size, None)
