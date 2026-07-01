"""
report_generator.py
Builds a downloadable PDF risk report using reportlab.
"""

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


def _get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="SectionHeading", parent=styles["Heading2"],
        textColor=colors.HexColor("#1F3B57"), spaceBefore=14, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="BodyJustified", parent=styles["BodyText"],
        alignment=4, spaceAfter=6
    ))
    return styles


def _risk_color(severity: str):
    return {
        "High": colors.HexColor("#D64545"),
        "Medium": colors.HexColor("#E0A400"),
        "Low": colors.HexColor("#3A8F4C"),
    }.get(severity, colors.grey)


def generate_pdf_report(filename: str, analysis: dict, output_path: str) -> str:
    """
    analysis is the dict produced by analyzer.analyze_document(), i.e. it
    contains 'clauses', 'risks', 'risk_score', and 'summary'.
    Returns the path of the generated PDF.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    styles = _get_styles()

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm
    )

    elements = []

    elements.append(Paragraph("Document Risk Analysis Report", styles["Title"]))
    elements.append(Paragraph(f"File: {filename}", styles["Normal"]))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]
    ))
    elements.append(Spacer(1, 0.5 * cm))

    clauses = analysis["clauses"]
    summary = analysis["summary"]
    risks = analysis["risks"]
    risk_score = analysis["risk_score"]

    # --- Overview table ---
    elements.append(Paragraph("Contract Overview", styles["SectionHeading"]))
    overview_data = [
        ["Contract Type", clauses.get("contract_type", "N/A")],
        ["Effective Date", clauses.get("effective_date", "N/A")],
        ["Expiry Date", clauses.get("expiry_date", "N/A")],
        ["Risk Score", f"{risk_score} / 100 ({summary.get('risk_band', 'N/A')})"],
    ]
    table = Table(overview_data, colWidths=[5 * cm, 10 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFF3F7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.4 * cm))

    # --- Executive summary ---
    elements.append(Paragraph("Executive Summary", styles["SectionHeading"]))
    elements.append(Paragraph(summary.get("executive_summary", ""), styles["BodyJustified"]))

    # --- Important clauses ---
    elements.append(Paragraph("Important Clauses", styles["SectionHeading"]))
    for item in summary.get("important_clauses", []):
        elements.append(Paragraph(f"<b>{item['clause']}:</b> {item['text']}", styles["BodyJustified"]))

    # --- Risks ---
    elements.append(Paragraph("Detected Risks", styles["SectionHeading"]))
    risk_data = [["Risk", "Severity", "Description"]]
    for r in risks:
        risk_data.append([r["risk"], r["severity"], r["description"]])

    risk_table = Table(risk_data, colWidths=[4 * cm, 2.2 * cm, 8.8 * cm], repeatRows=1)
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3B57")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for i, r in enumerate(risks, start=1):
        style_commands.append(("TEXTCOLOR", (1, i), (1, i), _risk_color(r["severity"])))
    risk_table.setStyle(TableStyle(style_commands))
    elements.append(risk_table)
    elements.append(Spacer(1, 0.4 * cm))

    # --- Recommendations ---
    elements.append(Paragraph("Recommendations", styles["SectionHeading"]))
    for rec in summary.get("recommendations", []):
        elements.append(Paragraph(f"• {rec}", styles["BodyJustified"]))

    doc.build(elements)
    return output_path