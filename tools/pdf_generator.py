import logging
import os
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from config.settings import COMPANY_NAME, RECEIPTS_DIR

logger = logging.getLogger(__name__)


def generate_pdf_receipt(
    order_id: int,
    user_name: str,
    product_name: str,
    technical_summary: str,
    final_price: float,
    human_spec: str,
    order_date: Optional[str] = None,
) -> str:
    """Generate a PDF receipt and return the file path."""
    import os
    os.makedirs(RECEIPTS_DIR, exist_ok=True)

    if order_date is None:
        order_date = datetime.utcnow().strftime("%B %d, %Y")

    file_path = os.path.join(RECEIPTS_DIR, f"receipt_{order_id}.pdf")
    logger.info(f"TOOL | generate_pdf_receipt | generating for order_id={order_id}")

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=28,
        textColor=colors.HexColor("#3B2314"),
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#7B5C3E"),
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#3B2314"),
        spaceBefore=12,
        spaceAfter=4,
        borderPad=4,
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        spaceAfter=4,
        leading=16,
    )
    price_style = ParagraphStyle(
        "Price",
        parent=styles["Normal"],
        fontSize=22,
        textColor=colors.HexColor("#3B2314"),
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=8,
    )

    elements = []

    # Header
    elements.append(Paragraph(COMPANY_NAME, title_style))
    elements.append(Paragraph("Premium Custom Furniture", subtitle_style))
    elements.append(Paragraph("Order Confirmation Receipt", subtitle_style))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#3B2314")))
    elements.append(Spacer(1, 0.3 * cm))

    # Order details table
    order_data = [
        ["Order ID", f"#{order_id}"],
        ["Date", order_date],
        ["Customer", user_name],
        ["Status", "Confirmed ✓"],
    ]
    order_table = Table(order_data, colWidths=[4 * cm, 12 * cm])
    order_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F5EDE3")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#3B2314")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D4B896")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(order_table)
    elements.append(Spacer(1, 0.4 * cm))

    # Product section
    elements.append(Paragraph("Product Selected", section_header_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D4B896")))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(f"<b>{product_name}</b>", body_style))
    elements.append(Spacer(1, 0.2 * cm))

    # Customer requirements
    elements.append(Paragraph("Customer Requirements", section_header_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D4B896")))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(human_spec, body_style))
    elements.append(Spacer(1, 0.2 * cm))

    # Technical specification
    elements.append(Paragraph("Technical Specification", section_header_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D4B896")))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(technical_summary, body_style))
    elements.append(Spacer(1, 0.4 * cm))

    # Price
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#3B2314")))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(f"Total Price: ${final_price:,.2f}", price_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#3B2314")))
    elements.append(Spacer(1, 0.4 * cm))

    # Footer
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#999999"),
        alignment=TA_CENTER,
    )
    elements.append(Paragraph(
        f"Thank you for choosing {COMPANY_NAME}. This receipt confirms your order. "
        "Our team will contact you within 2 business days to discuss production timelines.",
        footer_style
    ))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(
        f"© {datetime.utcnow().year} {COMPANY_NAME} | Enterprise Furniture Solutions",
        footer_style
    ))

    doc.build(elements)
    logger.info(f"TOOL | generate_pdf_receipt | PDF generated at {file_path}")
    return file_path
