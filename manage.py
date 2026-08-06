#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # Lit .env AVANT le setdefault ci-dessous : sans ça, DJANGO_SETTINGS_MODULE=...
    # dans .env est ignoré par toute commande manage.py lancée manuellement (le
    # service systemd, lui, s'en sort car EnvironmentFile= l'exporte comme
    # vraie variable d'environnement) — silencieusement retombé sur
    # `development` en production, sans aucune erreur visible.
    try:
        import environ

        environ.Env.read_env(Path(__file__).resolve().parent / ".env")
    except ImportError:
        pass
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
