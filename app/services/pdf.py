from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models import Hisab


def build_hisab_pdf(hisab: Hisab) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=hisab.title)
    styles = getSampleStyleSheet()

    rows = [["Item", "Amount"]]
    for expense in hisab.expenses:
        rows.append([expense.item_name, f"Rs. {expense.amount:,.2f}"])
    rows.append(["Total", f"Rs. {hisab.total_amount:,.2f}"])

    table = Table(rows, colWidths=[330, 140])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#ecfeff")),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
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

    receipt_items = [expense for expense in hisab.expenses if expense.receipt_url]
    if receipt_items:
        story.extend([Spacer(1, 18), Paragraph("Receipt Links", styles["Heading2"])])
        for expense in receipt_items:
            story.append(Paragraph(f"{expense.item_name}: {expense.receipt_url}", styles["Normal"]))

    doc.build(story)
    return buffer.getvalue()

