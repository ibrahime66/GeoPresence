import secrets

from django.db import migrations


def backfill_qr_token(apps, schema_editor):
    # RM-QR-001 : les agences déjà existantes n'ont pas déclenché le save()
    # (qui génère le jeton) de la migration précédente — sans ce backfill,
    # AgencyQRView planterait (reverse() d'une URL avec un jeton vide).
    Agency = apps.get_model("agencies", "Agency")
    for agency in Agency.all_objects.filter(qr_token="").iterator():
        agency.qr_token = secrets.token_urlsafe(24)
        agency.save(update_fields=["qr_token"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("agencies", "0007_agency_qr_token"),
    ]

    operations = [
        migrations.RunPython(backfill_qr_token, noop_reverse),
    ]
