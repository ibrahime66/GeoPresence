"""Chiffrement AES-256-GCM des sauvegardes — CDC §18.4.3.

AES-256-GCM plutôt que Fernet (déjà utilisé pour `FIELD_ENCRYPTION_KEY`,
cf. apps/core/encrypted_fields.py) : Fernet chiffre en AES-128, alors que le
CDC demande explicitement de l'AES-256 pour les sauvegardes.
"""

import base64
import hashlib
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE = 12


class BackupEncryptionError(Exception):
    pass


def _get_key():
    raw = settings.BACKUP_ENCRYPTION_KEY
    if not raw:
        raise ImproperlyConfigured(
            "BACKUP_ENCRYPTION_KEY n'est pas configurée — impossible de chiffrer/déchiffrer une sauvegarde."
        )
    key = base64.b64decode(raw)
    if len(key) != 32:
        raise ImproperlyConfigured("BACKUP_ENCRYPTION_KEY doit décoder en exactement 32 octets (AES-256).")
    return key


def encrypt_bytes(data: bytes) -> bytes:
    aesgcm = AESGCM(_get_key())
    nonce = os.urandom(NONCE_SIZE)
    return nonce + aesgcm.encrypt(nonce, data, None)


def decrypt_bytes(blob: bytes) -> bytes:
    if len(blob) < NONCE_SIZE:
        raise BackupEncryptionError("Fichier de sauvegarde corrompu ou tronqué.")
    nonce, ciphertext = blob[:NONCE_SIZE], blob[NONCE_SIZE:]
    aesgcm = AESGCM(_get_key())
    try:
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:  # cryptography lève InvalidTag — clé erronée ou fichier altéré.
        raise BackupEncryptionError("Échec du déchiffrement — clé incorrecte ou fichier altéré.") from exc


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
