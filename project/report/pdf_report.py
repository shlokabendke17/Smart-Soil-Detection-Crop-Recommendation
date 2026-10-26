"""
pdf_report.py
Builds the final AI-generated PDF report from all pipeline outputs.
"""

import datetime
import glob
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.i18n import t

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(HERE, "fonts")


def _register_devanagari_font():
    """Looks for a bundled Devanagari-capable TTF (e.g. Noto Sans Devanagari)
    in report/fonts/. Returns the registered font name, or None if not found.
    Hindi/Marathi glyphs cannot render with the built-in PDF base fonts
    (Helvetica etc. only cover Latin script), so without this font the
    report gracefully falls back to English text — see generate_report()."""
    candidates = glob.glob(os.path.join(FONTS_DIR, "*.ttf"))
    if not candidates:
        return None
    font_path = candidates[0]
    font_name = "DevanagariUnicode"
    try:
        pdfmetrics.registerFont(TTFont(font_name, font_path))
        return font_name
    except Exception:
        return None


def _styles(font_name: str = None):
    styles = getSampleStyleSheet()
    base_bold = font_name or "Helvetica-Bold"
    base_regular = font_name or "Helvetica"

    styles.add(ParagraphStyle(name="ReportTitle", fontSize=18, leading=22,
                               spaceAfter=6, textColor=colors.HexColor("#1b5e20"),
                               fontName=base_bold))
    styles.add(ParagraphStyle(name="Section", fontSize=13, leading=16,
                               spaceBefore=14, spaceAfter=6,
                               textColor=colors.HexColor("#2e7d32"),
                               fontName=base_bold))
    styles.add(ParagraphStyle(name="Body", fontSize=10.5, leading=15,
                               fontName=base_regular))
    styles.add(ParagraphStyle(name="Small", fontSize=8.5, leading=12,
                               textColor=colors.grey, fontName=base_regular))
    return styles


def generate_report(output_path: str, lang: str, payload: dict):
    """
    payload keys expected:
      soil_params: {ph, n, p, k}
      weather: {temperature, humidity, rainfall}
      cnn_result: {soil_type, confidence, method} or None
      health: {score, level, breakdown}
      crops: [{crop, probability}, ...]
      fertilizer: [{nutrient, status, fertilizer, reason}, ...]
      advisory: [str, ...]
      alerts: [str, ...]
    """
    font_note = None
    if lang in ("hi", "mr"):
        font_name = _register_devanagari_font()
        if font_name is None:
            font_note = (
                "Note: a Devanagari-script font was not found in report/fonts/, "
                "so this report is shown in English. Add a Unicode Devanagari "
                "TTF (e.g. Noto Sans Devanagari) to report/fonts/ to enable "
                "Hindi/Marathi rendering."
            )
            lang = "en"
    else:
        font_name = None

    styles = _styles(font_name)
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                             leftMargin=1.8 * cm, rightMargin=1.8 * cm)
    story = []

    if font_note:
        story.append(Paragraph(font_note, styles["Small"]))
        story.append(Spacer(1, 6))

    # Title
    story.append(Paragraph(t("report_title", lang), styles["ReportTitle"]))
    story.append(Paragraph(
        f"{t('generated_on', lang)}: {datetime.datetime.now().strftime('%d %b %Y, %H:%M')}",
        styles["Small"]))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#2e7d32"), thickness=1.2))
    story.append(Spacer(1, 10))

    # CNN reference block
    cnn = payload.get("cnn_result")
    if cnn:
        story.append(Paragraph(t("soil_type_cnn", lang), styles["Section"]))
        story.append(Paragraph(
            f"{cnn['soil_type']} — {cnn['confidence']}% {t('confidence', lang)} "
            f"<font size=8 color='grey'>({cnn.get('method', 'CNN')})</font>",
            styles["Body"]))
        story.append(Paragraph(
            "<i>Shown for reference only — not used in crop or fertilizer decisions below.</i>",
            styles["Small"]))

    # Soil parameters
    sp = payload["soil_params"]
    wt = payload["weather"]
    story.append(Paragraph(t("soil_parameters", lang), styles["Section"]))
    param_table = Table([
        ["pH", "Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"],
        [sp["ph"], sp["n"], sp["p"], sp["k"]],
    ], colWidths=[4 * cm] * 4)
    param_table.setStyle(_grid_style())
    story.append(param_table)

    story.append(Paragraph(t("weather_conditions", lang), styles["Section"]))
    weather_table = Table([
        ["Temperature (°C)", "Humidity (%)", "Rainfall (mm)"],
        [wt["temperature"], wt["humidity"], wt["rainfall"]],
    ], colWidths=[5.3 * cm] * 3)
    weather_table.setStyle(_grid_style())
    story.append(weather_table)

    # Soil health score
    health = payload["health"]
    story.append(Paragraph(t("soil_health_score", lang), styles["Section"]))
    story.append(Paragraph(
        f"<b>{health['score']} / 100</b> — {health['level']}", styles["Body"]))
    bd = health["breakdown"]
    bd_table = Table([
        ["pH", "N", "P", "K"],
        [f"{bd['ph']}/25", f"{bd['nitrogen']}/25", f"{bd['phosphorus']}/25", f"{bd['potassium']}/25"],
    ], colWidths=[4 * cm] * 4)
    bd_table.setStyle(_grid_style())
    story.append(bd_table)

    # Crop recommendations
    story.append(Paragraph(t("recommended_crops", lang), styles["Section"]))
    crop_rows = [["#", "Crop", t("confidence", lang).capitalize()]]
    for i, c in enumerate(payload["crops"], 1):
        crop_rows.append([str(i), c["crop"].title(), f"{c['probability']}%"])
    crop_table = Table(crop_rows, colWidths=[1.5 * cm, 8 * cm, 5.5 * cm])
    crop_table.setStyle(_grid_style(header=True))
    story.append(crop_table)

    # Fertilizer advice
    story.append(Paragraph(t("fertilizer_advice", lang), styles["Section"]))
    for f in payload["fertilizer"]:
        story.append(Paragraph(
            f"<b>{f['nutrient']} ({f['status']}):</b> {f['fertilizer']} — "
            f"<font size=9 color='grey'>{f['reason']}</font>", styles["Body"]))

    # Nutrient / soil improvement advisory
    story.append(Paragraph(t("soil_improvement", lang), styles["Section"]))
    for a in payload["advisory"]:
        story.append(Paragraph(f"• {a}", styles["Body"]))

    # Risk alerts
    story.append(Paragraph(t("risk_alerts", lang), styles["Section"]))
    alerts = payload["alerts"]
    if alerts:
        for al in alerts:
            story.append(Paragraph(f"[!] {al}", styles["Body"]))
    else:
        story.append(Paragraph(t("no_alerts", lang), styles["Body"]))

    # Disclaimer
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", color=colors.grey, thickness=0.5))
    story.append(Spacer(1, 6))
    story.append(Paragraph(t("disclaimer", lang), styles["Small"]))

    doc.build(story)
    return output_path


def _grid_style(header: bool = False):
    style = [
        ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#bdbdbd")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f5e9")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    return TableStyle(style)
