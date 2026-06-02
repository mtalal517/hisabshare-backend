from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.config import get_settings
from app.models import Hisab


def receipt_path_from_url(receipt_url: str | None) -> Path | None:
    if not receipt_url:
        return None

    upload_prefix = "/uploads/"
    if not receipt_url.startswith(upload_prefix):
        return None

    filename = Path(receipt_url.removeprefix(upload_prefix)).name
    if not filename:
        return None

    return Path(get_settings().upload_dir) / filename


def build_receipt_image(path: Path) -> Image | None:
    if not path.exists() or not path.is_file():
        return None

    try:
        image = Image(str(path))
    except Exception:
        return None
    max_width = 430
    max_height = 260
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight, 1)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    return image


def build_hisab_pdf(hisab: Hisab) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=hisab.title)
    styles = getSampleStyleSheet()

    rows = [["Item", "Amount", "Receipt"]]
    for expense in hisab.expenses:
        rows.append([expense.item_name, f"Rs. {expense.amount:,.2f}", "Attached" if expense.receipt_url else "-"])
    rows.append(["Total", f"Rs. {hisab.total_amount:,.2f}", ""])

    table = Table(rows, colWidths=[285, 115, 70])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#01858A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#DFF7F4")),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("ALIGN", (2, 1), (2, -1), "CENTER"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story = [
        Paragraph("HisabShare", styles["Title"]),
        Paragraph(hisab.title, styles["Heading2"]),
        Paragraph(f"Person: {hisab.person_name}", styles["Normal"]),
        Spacer(1, 16),
        table,
    ]

    receipt_items = [expense for expense in hisab.expenses if receipt_path_from_url(expense.receipt_url)]
    if receipt_items:
        story.extend([Spacer(1, 18), Paragraph("Receipts", styles["Heading2"])])
        for expense in receipt_items:
            receipt_path = receipt_path_from_url(expense.receipt_url)
            receipt_image = build_receipt_image(receipt_path) if receipt_path else None
            if receipt_image:
                story.append(
                    KeepTogether(
                        [
                            Paragraph(expense.item_name, styles["Heading3"]),
                            Spacer(1, 6),
                            receipt_image,
                            Spacer(1, 14),
                        ]
                    )
                )
            elif expense.receipt_url:
                story.append(Paragraph(f"{expense.item_name}: Receipt image unavailable", styles["Normal"]))

    doc.build(story)
    return buffer.getvalue()
