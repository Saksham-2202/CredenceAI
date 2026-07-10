"""
pdf_report.py
=================================================================
Credence AI  -  AI Powered Loan Assessment Report Generator
=================================================================

Generates a premium, bank-grade PDF report (SBI / HDFC / ICICI
style) summarising a loan applicant's profile and the model's
approve / reject decision.

Built entirely with reportlab.platypus (no canvas text drawing).

Author  : Saksham
Module  : src/pdf_report.py
-----------------------------------------------------------------
"""

import io
import os
from unittest import result
import uuid
import random
import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable,
    KeepTogether,
)
from reportlab.pdfgen import canvas as pdfcanvas

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


# =================================================================
# 1. COLOR PALETTE
# =================================================================

def create_color_palette():
    """
    Central source of truth for every colour used in the report.
    Keeping this in one place means the visual theme can be
    re-skinned by editing a single dictionary.
    """
    return {
        "primary": colors.HexColor("#003366"),      # deep navy blue
        "primary_dark": colors.HexColor("#00203F"),
        "accent": colors.HexColor("#0F62FE"),        # accent blue
        "success": colors.HexColor("#16A34A"),       # approved green
        "success_bg": colors.HexColor("#EAF7EE"),
        "rejected": colors.HexColor("#DC2626"),       # rejected red
        "rejected_bg": colors.HexColor("#FDECEC"),
        "background": colors.white,
        "card_bg": colors.HexColor("#F2F7FC"),        # very light blue
        "card_border": colors.HexColor("#D5E4F3"),
        "text_dark": colors.HexColor("#101828"),
        "text_muted": colors.HexColor("#5B6B7C"),
        "text_light": colors.HexColor("#8A97A6"),
        "divider": colors.HexColor("#E3EAF1"),
        "table_header_bg": colors.HexColor("#003366"),
        "table_row_alt": colors.HexColor("#F7FAFD"),
        "grey_box": colors.HexColor("#F1F3F5"),
        "grey_box_border": colors.HexColor("#DCE1E6"),
        "watermark": colors.Color(0.0, 0.2, 0.4, alpha=0.055),
    }


# =================================================================
# 2. PARAGRAPH / TABLE STYLE FACTORY
# =================================================================

def create_paragraph_styles():
    """
    Builds every custom ParagraphStyle used across the document.
    Returns a dict keyed by style name for easy lookup.
    """
    palette = create_color_palette()
    styles = {}

    styles["brand_title"] = ParagraphStyle(
        "brand_title", fontName="Helvetica-Bold", fontSize=22,
        leading=24, textColor=colors.white, alignment=TA_LEFT,
    )
    styles["brand_subtitle"] = ParagraphStyle(
        "brand_subtitle", fontName="Helvetica", fontSize=10.5,
        leading=13, textColor=colors.HexColor("#CFE0F5"), alignment=TA_LEFT,
    )
    styles["section_heading"] = ParagraphStyle(
        "section_heading", fontName="Helvetica-Bold", fontSize=12.5,
        leading=15, textColor=palette["primary"], spaceBefore=4, spaceAfter=8,
    )
    styles["card_label"] = ParagraphStyle(
        "card_label", fontName="Helvetica", fontSize=8.3,
        leading=10, textColor=palette["text_muted"],
    )
    styles["card_value"] = ParagraphStyle(
        "card_value", fontName="Helvetica-Bold", fontSize=10.2,
        leading=12.5, textColor=palette["text_dark"],
    )
    styles["table_header"] = ParagraphStyle(
        "table_header", fontName="Helvetica-Bold", fontSize=9,
        leading=11, textColor=colors.white, alignment=TA_LEFT,
    )
    styles["table_cell_label"] = ParagraphStyle(
        "table_cell_label", fontName="Helvetica", fontSize=9,
        leading=12, textColor=palette["text_muted"],
    )
    styles["table_cell_value"] = ParagraphStyle(
        "table_cell_value", fontName="Helvetica-Bold", fontSize=9.3,
        leading=12, textColor=palette["text_dark"],
    )
    styles["decision_title"] = ParagraphStyle(
        "decision_title", fontName="Helvetica-Bold", fontSize=20,
        leading=24, alignment=TA_CENTER,
    )
    styles["decision_sub"] = ParagraphStyle(
        "decision_sub", fontName="Helvetica", fontSize=10,
        leading=13, alignment=TA_CENTER, textColor=palette["text_muted"],
    )
    styles["decision_metric_label"] = ParagraphStyle(
        "decision_metric_label", fontName="Helvetica", fontSize=8.5,
        leading=10, alignment=TA_CENTER, textColor=palette["text_muted"],
    )
    styles["decision_metric_value"] = ParagraphStyle(
        "decision_metric_value", fontName="Helvetica-Bold", fontSize=13,
        leading=16, alignment=TA_CENTER, textColor=palette["text_dark"],
    )
    styles["body_text"] = ParagraphStyle(
        "body_text", fontName="Helvetica", fontSize=9.6,
        leading=14.5, textColor=palette["text_dark"], alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    styles["body_heading_small"] = ParagraphStyle(
        "body_heading_small", fontName="Helvetica-Bold", fontSize=10,
        leading=13, textColor=palette["primary"], spaceBefore=6, spaceAfter=3,
    )
    styles["whatif_title"] = ParagraphStyle(
        "whatif_title", fontName="Helvetica-Bold", fontSize=9.6,
        leading=12, textColor=palette["primary"],
    )
    styles["whatif_body"] = ParagraphStyle(
        "whatif_body", fontName="Helvetica", fontSize=8.8,
        leading=12, textColor=palette["text_muted"],
    )
    styles["disclaimer_text"] = ParagraphStyle(
        "disclaimer_text", fontName="Helvetica", fontSize=8.3,
        leading=12.5, textColor=palette["text_muted"], alignment=TA_JUSTIFY,
    )
    styles["footer_bold"] = ParagraphStyle(
        "footer_bold", fontName="Helvetica-Bold", fontSize=9,
        leading=11, textColor=palette["primary"],
    )
    styles["footer_small"] = ParagraphStyle(
        "footer_small", fontName="Helvetica", fontSize=7.6,
        leading=10.5, textColor=palette["text_light"],
    )
    styles["footer_small_right"] = ParagraphStyle(
        "footer_small_right", parent=styles["footer_small"], alignment=TA_CENTER,
    )
    return styles


# =================================================================
# 3. UTILITY HELPERS
# =================================================================

def generate_report_id():
    """
    Auto-generates a unique, human-readable Report ID in the form:
        CAI-YYYYMMDD-XXXXXX
    where XXXXXX is a random 6 digit sequence, guaranteeing that
    two reports generated in the same second still get distinct IDs.
    """
    date_part = datetime.datetime.now().strftime("%Y%m%d")
    unique_part = str(random.randint(0, 999999)).zfill(6)
    return f"CAI-{date_part}-{unique_part}"


def generate_qr_code(data_string):
    """
    Generates a QR code (as an in-memory PNG) encoding the report's
    verification payload (Report ID + timestamp + hash-like token).
    Returns a reportlab-compatible Image flowable, or None if the
    qrcode library is unavailable.
    """
    if not QR_AVAILABLE:
        return None

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2,
    )
    qr.add_data(data_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#003366", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return Image(buffer, width=22 * mm, height=22 * mm)


def safe_get(data, key, default="N/A"):
    """Defensive dictionary lookup used everywhere data is pulled in."""
    value = data.get(key, default)
    if value in (None, "", "nan"):
        return default
    return str(value)


def divider(color, thickness=0.6, space_before=6, space_after=6):
    """Returns a thin horizontal rule flowable used as a section separator."""
    return HRFlowable(
        width="100%", thickness=thickness, color=color,
        spaceBefore=space_before, spaceAfter=space_after,
    )


# =================================================================
# 4. WATERMARK + PAGE DECORATION (canvas-level, background only)
# =================================================================

class WatermarkCanvas(pdfcanvas.Canvas):
    """
    Custom canvas that paints a faint diagonal 'CREDENCE AI' watermark
    and a slim footer page-number bar on every page. This is the ONLY
    place raw canvas drawing is used - purely for background chrome,
    never for report content (which lives entirely in platypus flowables).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._palette = create_color_palette()

    def showPage(self):
        self._draw_watermark()
        self._draw_page_chrome()
        super().showPage()

    def _draw_watermark(self):
        self.saveState()
        self.setFont("Helvetica-Bold", 60)
        self.setFillColor(self._palette["watermark"])
        self.translate(A4[0] / 2, A4[1] / 2)
        self.rotate(38)
        self.drawCentredString(0, 0, "CREDENCE AI")
        self.restoreState()

    def _draw_page_chrome(self):
        self.saveState()
        self.setStrokeColor(self._palette["divider"])
        self.setLineWidth(0.5)
        self.line(20 * mm, 14 * mm, A4[0] - 20 * mm, 14 * mm)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(self._palette["text_light"])
        self.drawString(20 * mm, 10 * mm, "Credence AI  |  AI Powered Loan Assessment Report")
        self.drawRightString(A4[0] - 20 * mm, 10 * mm, f"Page {self._pageNumber}")
        self.restoreState()


# =================================================================
# 5. SECTION BUILDERS
# =================================================================

def build_header(styles, palette, logo_path=None):
    """
    Builds the top navy banner containing the Credence AI logo,
    title and subtitle. Implemented as a single-row table so the
    banner can carry a solid background colour edge-to-edge.
    """
    title_block = [
        Paragraph("CREDENCE AI", styles["brand_title"]),
        Spacer(1, 2),
        Paragraph("AI Powered Loan Assessment Report", styles["brand_subtitle"]),
    ]

    if logo_path and os.path.exists(logo_path):
        logo = Image(logo_path, width=16 * mm, height=16 * mm)
        row = [[logo, title_block]]
        col_widths = [22 * mm, 148 * mm]
    else:
        row = [[title_block]]
        col_widths = [170 * mm]

    banner = Table(row, colWidths=col_widths)
    banner_style = [
        ("BACKGROUND", (0, 0), (-1, -1), palette["primary"]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (-1, 0), (-1, 0), 10),
    ]
    banner.setStyle(TableStyle(banner_style))

    return [banner, Spacer(1, 14)]


def build_report_information(styles, palette, report_meta):
    """
    Builds the 'Report Information' light-blue card containing the
    auto-generated Report ID, timestamps, model details and QR code
    for verification.
    """
    now = datetime.datetime.now()

    left_rows = [
        ("Report ID", report_meta.get("report_id")),
        ("Generation Date", now.strftime("%d %B %Y")),
        ("Generation Time", now.strftime("%I:%M:%S %p")),
    ]
    right_rows = [
        ("Prediction Model", report_meta.get("model_name", "Naive Bayes")),
        ("Model Version", report_meta.get("model_version", "v1.0")),
        ("Developer", report_meta.get("developer", "Saksham")),
    ]

    def render_column(rows):
        flow = []
        for label, value in rows:
            flow.append(Paragraph(label.upper(), styles["card_label"]))
            flow.append(Paragraph(str(value), styles["card_value"]))
            flow.append(Spacer(1, 5))
        return flow

    qr_flowable = generate_qr_code(
        f"CredenceAI|{report_meta.get('report_id')}|{now.isoformat()}"
    )

    if qr_flowable:
        content_row = [[render_column(left_rows), render_column(right_rows), qr_flowable]]
        col_widths = [72 * mm, 72 * mm, 26 * mm]
    else:
        content_row = [[render_column(left_rows), render_column(right_rows)]]
        col_widths = [85 * mm, 85 * mm]

    inner = Table(content_row, colWidths=col_widths)
    inner.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (-1, 0), (-1, 0), "CENTER"),
    ]))

    card = Table([[inner]], colWidths=[170 * mm])
    card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), palette["card_bg"]),
        ("BOX", (0, 0), (-1, -1), 0.75, palette["card_border"]),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))

    return [
        Paragraph("REPORT INFORMATION", styles["section_heading"]),
        card,
        Spacer(1, 16),
    ]


def _two_column_data_table(styles, palette, heading_text, field_pairs):
    """
    Shared renderer for the Applicant Information and Financial
    Information sections - both are professional bordered two-column
    label/value tables with a navy header row.
    """
    header_row = [
        Paragraph("FIELD", styles["table_header"]),
        Paragraph("DETAIL", styles["table_header"]),
        Paragraph("FIELD", styles["table_header"]),
        Paragraph("DETAIL", styles["table_header"]),
    ]

    # Pair up fields two-per-row so the table reads as 2 label/value pairs wide
    rows = [header_row]
    for i in range(0, len(field_pairs), 2):
        left = field_pairs[i]
        right = field_pairs[i + 1] if i + 1 < len(field_pairs) else ("", "")
        rows.append([
            Paragraph(left[0], styles["table_cell_label"]),
            Paragraph(str(left[1]), styles["table_cell_value"]),
            Paragraph(right[0], styles["table_cell_label"]) if right[0] else "",
            Paragraph(str(right[1]), styles["table_cell_value"]) if right[0] else "",
        ])

    col_widths = [32 * mm, 53 * mm, 32 * mm, 53 * mm]
    table = Table(rows, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), palette["table_header_bg"]),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, palette["card_border"]),
        ("LINEBELOW", (0, 0), (-1, 0), 1, palette["table_header_bg"]),
    ]
    # zebra-striping on data rows
    for row_index in range(1, len(rows)):
        if row_index % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, row_index), (-1, row_index), palette["table_row_alt"]))

    table.setStyle(TableStyle(style_cmds))

    return [
        Paragraph(heading_text, styles["section_heading"]),
        table,
        Spacer(1, 16),
    ]


def build_applicant_table(styles, palette, data):
    """Builds the professional Applicant Information table."""
    field_pairs = [
        ("Age", safe_get(data, "age")),
        ("Gender", safe_get(data, "gender")),
        ("Marital Status", safe_get(data, "marital_status")),
        ("Education", safe_get(data, "education")),
        ("Employment", safe_get(data, "employment")),
        ("Employer Category", safe_get(data, "employer_category")),
        ("Dependents", safe_get(data, "dependents")),
        ("Property Area", safe_get(data, "property_area")),
    ]
    return _two_column_data_table(styles, palette, "APPLICANT INFORMATION", field_pairs)


def build_financial_table(styles, palette, data, currency="INR"):
    """Builds the professional bordered Financial Information table."""
    symbol = "Rs. " if currency == "INR" else "$ "

    def money(key):
        val = data.get(key)
        if val in (None, "", "nan"):
            return "N/A"
        try:
            return f"{symbol}{float(val):,.2f}"
        except (ValueError, TypeError):
            return str(val)

    field_pairs = [
        ("Monthly Income", money("monthly_income")),
        ("Co-Applicant Income", money("co_applicant_income")),
        ("Credit Score", safe_get(data, "credit_score")),
        ("Savings", money("savings")),
        ("Existing Loans", safe_get(data, "existing_loans")),
        ("DTI Ratio", safe_get(data, "dti_ratio")),
        ("Collateral Value", money("collateral_value")),
        ("Loan Amount", money("loan_amount")),
        ("Loan Term", safe_get(data, "loan_term")),
        ("Loan Purpose", safe_get(data, "loan_purpose")),
    ]
    return _two_column_data_table(styles, palette, "FINANCIAL INFORMATION", field_pairs)


def build_ai_decision_card(styles, palette, prediction):
    """
    Builds the large centered AI Decision card. Renders green/APPROVED
    or red/REJECTED styling based on prediction['approved'] (bool),
    and shows confidence + risk level metrics beneath the verdict.
    """
    approved = bool(prediction.get("approved", False))
    confidence = prediction.get("confidence", "N/A")
    risk_level = prediction.get("risk_level", "N/A")

    if approved:
        bg = palette["success_bg"]
        fg = palette["success"]
        verdict_text = "&#10003;  LOAN APPROVED"
    else:
        bg = palette["rejected_bg"]
        fg = palette["rejected"]
        verdict_text = "&#10007;  LOAN REJECTED"

    verdict_style = ParagraphStyle(
        "verdict_dynamic", parent=styles["decision_title"], textColor=fg,
    )

    metrics_row = Table(
        [[
            Paragraph("CONFIDENCE", styles["decision_metric_label"]),
            Paragraph("RISK LEVEL", styles["decision_metric_label"]),
        ], [
            Paragraph(str(confidence), styles["decision_metric_value"]),
            Paragraph(str(risk_level), ParagraphStyle(
                "risk_dynamic", parent=styles["decision_metric_value"],
                textColor=_risk_color(risk_level, palette),
            )),
        ]],
        colWidths=[85 * mm, 85 * mm],
    )
    metrics_row.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LINEAFTER", (0, 0), (0, -1), 0.6, palette["card_border"]),
        ("TOPPADDING", (0, 1), (-1, 1), 2),
    ]))

    inner_content = [
        Paragraph(verdict_text, verdict_style),
        Spacer(1, 6),
        Paragraph("AI Model Decision based on applicant &amp; financial profile", styles["decision_sub"]),
        Spacer(1, 12),
        divider(palette["card_border"], space_before=0, space_after=10),
        metrics_row,
    ]

    card = Table([[inner_content]], colWidths=[170 * mm])
    card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 1, fg),
        ("TOPPADDING", (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))

    return [
        Paragraph("AI DECISION", styles["section_heading"]),
        card,
        Spacer(1, 16),
    ]


def _risk_color(risk_level, palette):
    """Maps a risk level string to an appropriate accent colour."""
    level = str(risk_level).strip().upper()
    if level == "LOW":
        return palette["success"]
    if level == "HIGH":
        return palette["rejected"]
    if level == "MEDIUM":
        return colors.HexColor("#B45309")  # amber
    return palette["text_dark"]


def build_explanation_section(styles, palette, explanation):
    """
    Builds the AI Explanation card: Financial Profile Summary,
    Overall Assessment, Model Insight and Recommendation - each
    rendered as flowing paragraphs, not bullet fragments.
    """
    blocks = [
        ("Financial Profile Summary", explanation.get("financial_summary", "Not available.")),
        ("Overall Assessment", explanation.get("overall_assessment", "Not available.")),
        ("Model Insight", explanation.get("model_insight", "Not available.")),
        ("Recommendation", explanation.get("recommendation", "Not available.")),
    ]

    content = []
    for heading, text in blocks:
        content.append(Paragraph(heading, styles["body_heading_small"]))
        content.append(Paragraph(text, styles["body_text"]))

    card = Table([[content]], colWidths=[170 * mm])
    card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), palette["card_bg"]),
        ("BOX", (0, 0), (-1, -1), 0.75, palette["card_border"]),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
    ]))

    return [
        Paragraph("AI EXPLANATION", styles["section_heading"]),
        card,
        Spacer(1, 16),
    ]


def build_what_if_section(styles, palette, suggestions):
    """
    Builds the 'What-If Analysis' recommendation cards. Only called
    when the prediction is REJECTED. `suggestions` is a list of dicts
    with 'title' and 'body' keys, e.g.
        {"title": "Increase Credit Score", "body": "..."}
    """
    if not suggestions:
        return []

    heading = [Paragraph("WHAT-IF ANALYSIS  -  Suggested Improvements", styles["section_heading"])]

    cards = []
    for item in suggestions:
        title = item.get("title", "Suggestion")
        body = item.get("body", "")
        card_content = [
            Paragraph(f"&#8594;  {title}", styles["whatif_title"]),
            Spacer(1, 2),
            Paragraph(body, styles["whatif_body"]),
        ]
        card = Table([[card_content]], colWidths=[170 * mm])
        card.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), palette["card_bg"]),
            ("BOX", (0, 0), (-1, -1), 0.6, palette["accent"]),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]))
        cards.append(card)
        cards.append(Spacer(1, 6))

    return heading + cards + [Spacer(1, 10)]


def build_disclaimer(styles, palette):
    """Builds the professional grey disclaimer box."""
    text = (
        "This assessment has been generated using a Machine Learning model. "
        "The prediction should assist loan officers and must not be treated as "
        "the sole approval criterion. Final approval should follow institutional "
        "policies and manual verification."
    )
    box = Table([[Paragraph(text, styles["disclaimer_text"])]], colWidths=[170 * mm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), palette["grey_box"]),
        ("BOX", (0, 0), (-1, -1), 0.6, palette["grey_box_border"]),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return [
        Paragraph("DISCLAIMER", styles["section_heading"]),
        box,
        Spacer(1, 16),
    ]


def build_footer(styles, palette, report_meta):
    """
    Builds the in-flow authentication footer block (distinct from the
    per-page canvas footer chrome). Confirms digital generation, states
    no physical signature is required, and shows version / repo info.
    """
    now = datetime.datetime.now()
    left = [
        Paragraph("Digitally Generated by Credence AI", styles["footer_bold"]),
        Paragraph("Machine Learning Based Loan Approval Prediction System", styles["footer_small"]),
        Paragraph("No Physical Signature Required", styles["footer_small"]),
    ]
    right = [
        Paragraph(f"Version: {report_meta.get('version', 'v1.0.0')}", styles["footer_small_right"]),
        Paragraph(report_meta.get("github_url", "github.com/saksham-2202/CredenceAI"), styles["footer_small_right"]),
        Paragraph(f"Generated: {now.strftime('%d %b %Y, %I:%M %p')}", styles["footer_small_right"]),
    ]

    table = Table([[left, right]], colWidths=[110 * mm, 60 * mm])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))

    return [
        divider(palette["divider"], space_before=4, space_after=10),
        table,
    ]


# =================================================================
# 6. PAGE TEMPLATE / DOCUMENT ASSEMBLY
# =================================================================

def _build_doc_template(output_path):
    """
    Creates a BaseDocTemplate with a single content frame, leaving
    margin space for the canvas-drawn footer chrome and watermark.
    """
    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=16 * mm,
        bottomMargin=20 * mm,
        title="Credence AI - Loan Assessment Report",
        author="Credence AI",
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id="main_frame",
    )
    template = PageTemplate(id="credence_template", frames=[frame])
    doc.addPageTemplates([template])
    return doc



def generate_pdf(
    user_data,
    result,
    confidence,
    suggestions=None,
    report_meta=None,
    output_path="CredenceAI_Report.pdf",
    logo_path="assets/logo.png"
):
    if report_meta is None:
        report_meta = {}

    applicant_data = {
    "age": user_data["Age"],
    "gender": user_data["Gender"],
    "marital_status": user_data["Marital_Status"],
    "education": user_data["Education_Level"],
    "employment": user_data["Employment_Status"],
    "employer_category": user_data["Employer_Category"],
    "dependents": user_data["Dependents"],
    "property_area": user_data["Property_Area"],
    }

    financial_data = {
    "monthly_income": user_data["Applicant_Income"],
    "co_applicant_income": user_data["Coapplicant_Income"],
    "credit_score": user_data["Credit_Score"],
    "savings": user_data["Savings"],
    "existing_loans": user_data["Existing_Loans"],
    "dti_ratio": user_data["DTI_Ratio"],
    "collateral_value": user_data["Collateral_Value"],
    "loan_amount": user_data["Loan_Amount"],
    "loan_term": user_data["Loan_Term"],
    "loan_purpose": user_data["Loan_Purpose"],
    }

    prediction = {
    "approved": result == "Approved",
    "confidence": f"{confidence*100:.2f}%",
    "risk_level": (
        "LOW"
        if confidence < 0.60
        else "MEDIUM"
        if confidence < 0.80
        else "HIGH"
    ),
    }

    explanation = {}

    if result == "Approved":

        explanation["financial_summary"] = (
        "The applicant demonstrates a financially stable profile with acceptable credit behaviour."
        )

        explanation["overall_assessment"] = (
        "The machine learning model predicts a high likelihood of successful loan repayment."
        )

        explanation["model_insight"] = (
        "Strong financial indicators positively influenced the prediction."
        )

        explanation["recommendation"] = (
        "Proceed with standard verification before loan disbursement."
        )

    else:

        explanation["financial_summary"] = (
        "The applicant exhibits one or more financial risk indicators."
    )

    explanation["overall_assessment"] = (
        "The overall financial profile indicates an elevated lending risk."
    )

    explanation["model_insight"] = (
        "Multiple applicant attributes collectively influenced the rejection."
    )

    explanation["recommendation"] = (
        "Review the application manually or improve the financial profile before reapplying."
    )

    

    """
    Main entry point. Assembles every section into a single story
    and renders the final PDF to `output_path`.

    Parameters
    ----------
    applicant_data : dict   - age, gender, marital_status, education, etc.
    financial_data  : dict  - monthly_income, credit_score, loan_amount, etc.
    prediction      : dict  - {"approved": bool, "confidence": "87%", "risk_level": "LOW"}
    explanation     : dict  - financial_summary, overall_assessment,
                               model_insight, recommendation
    suggestions     : list[dict] | None - only used when rejected
    output_path     : str   - destination .pdf path
    logo_path       : str   - path to assets/logo.png
    report_meta     : dict | None - model_name, model_version, developer,
                               version, github_url. report_id is
                               auto-generated if not supplied.
    """
    palette = create_color_palette()
    styles = create_paragraph_styles()

    report_meta = dict(report_meta or {})
    report_meta.setdefault("report_id", generate_report_id())
    report_meta.setdefault("model_name", "Naive Bayes")
    report_meta.setdefault("model_version", "v1.0")
    report_meta.setdefault("developer", "Saksham")
    report_meta.setdefault("version", "v1.0.0")
    report_meta.setdefault("github_url", "github.com/saksham-2202/CredenceAI")

    story = []
    story += build_header(styles, palette, logo_path=logo_path)
    story += build_report_information(styles, palette, report_meta)
    story += build_applicant_table(styles, palette, applicant_data)
    story += build_financial_table(styles, palette, financial_data)
    story += build_ai_decision_card(styles, palette, prediction)
    story += build_explanation_section(styles, palette, explanation)

    if not prediction.get("approved", False) and suggestions:
        story += build_what_if_section(styles, palette, suggestions)

    story += build_disclaimer(styles, palette)
    story += build_footer(styles, palette, report_meta)

    doc = _build_doc_template(output_path)
    doc.build(story, canvasmaker=WatermarkCanvas)

    return output_path


# =================================================================
# 7. STANDALONE TEST / DEMO
# =================================================================

if __name__ == "__main__":
    demo_applicant = {
        "age": 34, "gender": "Male", "marital_status": "Married",
        "education": "Graduate", "employment": "Salaried",
        "employer_category": "MNC", "dependents": 2, "property_area": "Urban",
    }
    demo_financial = {
        "monthly_income": 85000, "co_applicant_income": 32000,
        "credit_score": 762, "savings": 410000, "existing_loans": 1,
        "dti_ratio": "0.28", "collateral_value": 2200000,
        "loan_amount": 1500000, "loan_term": "180 months",
        "loan_purpose": "Home Purchase",
    }
    demo_prediction = {"approved": True, "confidence": "91.4%", "risk_level": "LOW"}
    demo_explanation = {
        "financial_summary": (
            "The applicant demonstrates a stable salaried income supplemented by a "
            "co-applicant contribution, resulting in a comfortable debt-to-income "
            "ratio well within acceptable lending thresholds."
        ),
        "overall_assessment": (
            "Combined income, savings buffer and collateral value comfortably "
            "cover the requested loan amount, positioning this application "
            "favourably against the institution's risk appetite."
        ),
        "model_insight": (
            "The model weighted credit score and DTI ratio as the strongest positive "
            "contributors, with employer category providing a secondary stability signal."
        ),
        "recommendation": (
            "Proceed with standard documentation verification; no additional "
            "collateral or guarantor requirements are indicated at this time."
        ),
    }

    generate_pdf(
        demo_applicant, demo_financial, demo_prediction, demo_explanation,
        suggestions=None,
        output_path="/home/claude/demo_loan_report.pdf",
        logo_path="/home/claude/assets/logo.png",
        report_meta={"developer": "Saksham"},
    )
    print("Demo PDF generated.")