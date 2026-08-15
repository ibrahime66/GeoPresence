"""Exports CSV/Excel/PDF génériques — CDC §18.3.

Générés de façon synchrone (téléchargement direct) plutôt qu'asynchrone via
Celery (absent du projet, cf. requirements/production.txt) : acceptable pour
les volumes actuels, à revoir si les exports deviennent lents sur de gros
tenants (bascule vers une tâche Celery + notification CDC §18.3 alors)."""

import csv
from io import BytesIO
from xml.sax.saxutils import escape as xml_escape

from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BRAND_NAVY = colors.HexColor("#0A1E45")
BRAND_GRID = colors.HexColor("#E4E7EC")
BRAND_STRIPE = colors.HexColor("#F8FAFC")

# Caractères qu'Excel/LibreOffice/Google Sheets interprètent comme un début de
# formule (=, +, -, @) : un commentaire libre saisi par un employé/manager
# (justificatif d'absence, commentaire de validation...) et repris tel quel
# dans un export CSV/XLSX exécuterait sinon une formule à l'ouverture du
# fichier (ex. =HYPERLINK(...), injection DDE) — cf. OWASP CSV Injection.
FORMULA_PREFIXES = ("=", "+", "-", "@")


def _sanitize_cell(value):
    if isinstance(value, str) and value.startswith(FORMULA_PREFIXES):
        return "'" + value
    return value


def _sanitize_row(row):
    return [_sanitize_cell(v) for v in row]


def export_csv(filename, headers, rows):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    # BOM UTF-8 : Excel n'interprète correctement les accents dans un CSV
    # que si le fichier commence par ce marqueur.
    response.write("﻿")
    writer = csv.writer(response)
    writer.writerow(headers)
    writer.writerows(_sanitize_row(row) for row in rows)
    return response


def export_xlsx(filename, headers, rows, sheet_title="Export"):
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_title[:31]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for row in rows:
        ws.append(_sanitize_row(row))
    for col_cells in ws.columns:
        length = max((len(str(c.value)) if c.value is not None else 0) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 40)

    buffer = BytesIO()
    wb.save(buffer)
    response = HttpResponse(
        buffer.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


PDF_HEADER_STYLE = ParagraphStyle("gp-pdf-header", fontSize=8, leading=10, textColor=colors.white, fontName="Helvetica-Bold")
PDF_CELL_STYLE = ParagraphStyle("gp-pdf-cell", fontSize=7.5, leading=9.5)


def _pdf_cell(value, style):
    """Enveloppe chaque valeur dans un Paragraph (au lieu d'une simple
    chaîne) pour que le texte retourne à la ligne DANS la largeur de colonne
    impartie plutôt que de déborder de la page sans erreur ni avertissement —
    un commentaire libre un peu long (justificatif d'absence, commentaire de
    validation...) rendait sinon les colonnes suivantes invisibles, hors
    page, silencieusement. xml_escape est nécessaire car Paragraph interprète
    son contenu comme un sous-ensemble de XML (contrairement à une simple
    chaîne de cellule Table) : un commentaire contenant '<' ou '&' casserait
    sinon le rendu."""
    text = "" if value is None else str(value)
    return Paragraph(xml_escape(text).replace("\n", "<br/>"), style)


def export_pdf(filename, title, headers, rows, subtitle=""):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), title=title, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    elements = [Paragraph(title, styles["Title"])]
    if subtitle:
        elements.append(Paragraph(subtitle, styles["Normal"]))
    elements.append(Spacer(1, 12))

    data = [[_pdf_cell(h, PDF_HEADER_STYLE) for h in headers]] + [
        [_pdf_cell(v, PDF_CELL_STYLE) for v in row] for row in rows
    ]
    col_width = doc.width / len(headers)
    table = Table(data, repeatRows=1, colWidths=[col_width] * len(headers))
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BRAND_NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, BRAND_GRID),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_STRIPE]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
