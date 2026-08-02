from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models


def _fernet():
    key = settings.FIELD_ENCRYPTION_KEY
    return Fernet(key.encode() if isinstance(key, str) else key)


class EncryptedCharField(models.CharField):
    """Chiffrement transparent au repos (Fernet = AES-128-CBC + HMAC) — CDC §13.6,
    RM-SEC-004. Le texte est chiffré à l'écriture et déchiffré à la lecture,
    de façon invisible pour le reste du code applicatif."""

    def __init__(self, *args, **kwargs):
        # Le texte chiffré est nettement plus long que le texte clair (overhead
        # Fernet + encodage) : on élargit systématiquement max_length en base.
        kwargs.setdefault("max_length", 500)
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if not value:
            return value
        return _fernet().encrypt(value.encode()).decode()

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            return _fernet().decrypt(value.encode()).decode()
        except InvalidToken:
            # Ne devrait pas arriver en fonctionnement normal ; on ne fait
            # jamais planter une lecture pour une donnée mal déchiffrable.
            return value
