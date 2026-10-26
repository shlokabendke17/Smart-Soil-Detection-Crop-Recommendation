"""
generate_samples.py
Generates realistic sample soil test reports (Soil Health Card PDF, Lab Report PDF,
Alkaline Black Soil PDF, and Field Telemetry CSV) in data/sample_reports/.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_reports"))
os.makedirs(SAMPLE_DIR, exist_ok=True)


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle(name="CardTitle", fontSize=16, leading=20, textColor=colors.HexColor("#1b5e20"), fontName="Helvetica-Bold"))
    ss.add(ParagraphStyle(name="CardSub", fontSize=10, leading=14, textColor=colors.HexColor("#333333"), fontName="Helvetica"))
    ss.add(ParagraphStyle(name="SecHeader", fontSize=12, leading=15, textColor=colors.HexColor("#2e7d32"), fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4))
    ss.add(ParagraphStyle(name="BodyP", fontSize=9, leading=13, fontName="Helvetica"))
    ss.add(ParagraphStyle(name="Th", fontSize=9, leading=11, fontName="Helvetica-Bold", textColor=colors.white))
    ss.add(ParagraphStyle(name="Td", fontSize=8.5, leading=11, fontName="Helvetica"))
    return ss


def create_soil_health_card():
    filepath = os.path.join(SAMPLE_DIR, "soil_health_card_maharashtra.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    st = _styles()
    story = []

    story.append(Paragraph("GOVERNMENT OF MAHARASHTRA — KRISHI VIGYAN KENDRA", st["CardSub"]))
    story.append(Paragraph("🌾 SOIL HEALTH CARD / मृदा स्वास्थ्य पत्रिका", st["CardTitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2e7d32"), spaceBefore=4, spaceAfter=8))

    meta_data = [
        [Paragraph("<b>Farmer Name:</b> Anand R. Shinde", st["BodyP"]), Paragraph("<b>Sample ID:</b> SHC-MH-PUN-2026-984", st["BodyP"])],
        [Paragraph("<b>District / State:</b> Pune, Maharashtra", st["BodyP"]), Paragraph("<b>Date of Issue:</b> 18-Sep-2026", st["BodyP"])],
        [Paragraph("<b>Soil Classification:</b> Clay Loam (Black Soil)", st["BodyP"]), Paragraph("<b>Survey / Gut No:</b> 142/3", st["BodyP"])],
    ]
    t_meta = Table(meta_data, colWidths=[260, 260])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f8e9")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#aed581")),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    story.append(Paragraph("🧪 1. Soil Chemical Composition (Macro & Secondary Nutrients)", st["SecHeader"]))
    chem_data = [
        [Paragraph("Parameter", st["Th"]), Paragraph("Tested Value", st["Th"]), Paragraph("Standard Unit", st["Th"]), Paragraph("Rating", st["Th"])],
        [Paragraph("Soil Reaction (pH)", st["Td"]), Paragraph("7.4", st["Td"]), Paragraph("pH Scale (0–14)", st["Td"]), Paragraph("Slightly Alkaline", st["Td"])],
        [Paragraph("Electrical Conductivity (EC)", st["Td"]), Paragraph("0.38", st["Td"]), Paragraph("dS/m", st["Td"]), Paragraph("Normal (Safe)", st["Td"])],
        [Paragraph("Organic Carbon (OC)", st["Td"]), Paragraph("0.58", st["Td"]), Paragraph("%", st["Td"]), Paragraph("Medium", st["Td"])],
        [Paragraph("Available Nitrogen (N)", st["Td"]), Paragraph("58.0", st["Td"]), Paragraph("kg/ha", st["Td"]), Paragraph("Medium Low", st["Td"])],
        [Paragraph("Available Phosphorus (P)", st["Td"]), Paragraph("38.0", st["Td"]), Paragraph("kg/ha", st["Td"]), Paragraph("Medium", st["Td"])],
        [Paragraph("Available Potassium (K)", st["Td"]), Paragraph("62.0", st["Td"]), Paragraph("kg/ha", st["Td"]), Paragraph("High", st["Td"])],
    ]
    t_chem = Table(chem_data, colWidths=[180, 110, 110, 120])
    t_chem.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e7d32")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c8e6c9")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fbe7")]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_chem)
    story.append(Spacer(1, 10))

    story.append(Paragraph("🌤️ 2. Regional Agro-Climatic Baseline Variables", st["SecHeader"]))
    agro_data = [
        [Paragraph("Variable", st["Th"]), Paragraph("Measured Baseline", st["Th"]), Paragraph("Unit", st["Th"]), Paragraph("Condition", st["Th"])],
        [Paragraph("Ambient Temperature", st["Td"]), Paragraph("28.0", st["Td"]), Paragraph("°C", st["Td"]), Paragraph("Warm", st["Td"])],
        [Paragraph("Relative Humidity", st["Td"]), Paragraph("68.0", st["Td"]), Paragraph("%", st["Td"]), Paragraph("Optimal", st["Td"])],
        [Paragraph("Expected Rainfall", st["Td"]), Paragraph("95.0", st["Td"]), Paragraph("mm", st["Td"]), Paragraph("Moderate Monsoon", st["Td"])],
    ]
    t_agro = Table(agro_data, colWidths=[180, 110, 110, 120])
    t_agro.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565c0")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbdefb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f7ff")]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_agro)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Certified Soil Analyst:</b> Dr. S. K. Mahajan (Senior Agronomist, KVK)", st["BodyP"]))
    story.append(Paragraph("<i>This document is an authenticated Soil Health Card copy for algorithmic automated ingestion.</i>", st["CardSub"]))

    doc.build(story)
    return filepath


def create_lab_report():
    filepath = os.path.join(SAMPLE_DIR, "agri_diagnostic_lab_report.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    st = _styles()
    story = []

    story.append(Paragraph("PRECISION AGRO-ANALYTICAL LABS & RESEARCH PVT LTD", st["CardSub"]))
    story.append(Paragraph("🧪 COMPREHENSIVE SOIL DIAGNOSTIC CERTIFICATE", st["CardTitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#00695c"), spaceBefore=4, spaceAfter=8))

    meta_data = [
        [Paragraph("<b>Client:</b> Greenfield Organic Farms", st["BodyP"]), Paragraph("<b>Lab Ref No:</b> LAB-AGR-88412", st["BodyP"])],
        [Paragraph("<b>Location:</b> Nashik Agricultural Zone", st["BodyP"]), Paragraph("<b>Analysis Date:</b> 22-Sep-2026", st["BodyP"])],
        [Paragraph("<b>Soil Type:</b> Loamy Soil", st["BodyP"]), Paragraph("<b>Sample Type:</b> Core Depth 0–20 cm", st["BodyP"])],
    ]
    t_meta = Table(meta_data, colWidths=[260, 260])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e0f2f1")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#80cbc4")),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    story.append(Paragraph("🔬 Certified Laboratory Analytical Parameters", st["SecHeader"]))
    params_data = [
        [Paragraph("Analyte", st["Th"]), Paragraph("Result", st["Th"]), Paragraph("Test Method", st["Th"]), Paragraph("Optimum Range", st["Th"])],
        [Paragraph("pH (1:2.5 w/v)", st["Td"]), Paragraph("6.8", st["Td"]), Paragraph("Potentiometric", st["Td"]), Paragraph("6.5 – 7.5", st["Td"])],
        [Paragraph("Nitrogen (N)", st["Td"]), Paragraph("72.0", st["Td"]), Paragraph("Alkaline Permanganate (kg/ha)", st["Td"]), Paragraph("50 – 100", st["Td"])],
        [Paragraph("Phosphorus (P)", st["Td"]), Paragraph("52.0", st["Td"]), Paragraph("Olsen Spectrophotometry (kg/ha)", st["Td"]), Paragraph("35 – 65", st["Td"])],
        [Paragraph("Potassium (K)", st["Td"]), Paragraph("48.0", st["Td"]), Paragraph("Flame Photometer (kg/ha)", st["Td"]), Paragraph("40 – 70", st["Td"])],
        [Paragraph("Temperature (°C)", st["Td"]), Paragraph("26.0", st["Td"]), Paragraph("Regional Weather Telemetry", st["Td"]), Paragraph("20 – 32", st["Td"])],
        [Paragraph("Humidity (%)", st["Td"]), Paragraph("75.0", st["Td"]), Paragraph("Hygrometric Sensor", st["Td"]), Paragraph("60 – 85", st["Td"])],
        [Paragraph("Precipitation / Rainfall (mm)", st["Td"]), Paragraph("130.0", st["Td"]), Paragraph("Seasonal Tipping Bucket", st["Td"]), Paragraph("80 – 200", st["Td"])],
    ]
    t_params = Table(params_data, colWidths=[160, 90, 160, 110])
    t_params.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00695c")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b2dfdb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0faf9")]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_params)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Quality Assurance:</b> ISO/IEC 17025 Accredited Agricultural Lab", st["BodyP"]))
    doc.build(story)
    return filepath


def create_alkaline_report():
    filepath = os.path.join(SAMPLE_DIR, "black_soil_alkaline_report.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    st = _styles()
    story = []

    story.append(Paragraph("COTTON & CASH CROP RESEARCH SUB-STATION", st["CardSub"]))
    story.append(Paragraph("🌿 BLACK COTTON SOIL AGRO-DIAGNOSTIC", st["CardTitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#d84315"), spaceBefore=4, spaceAfter=8))

    meta_data = [
        [Paragraph("<b>Farmer:</b> Devidas Deshmukh", st["BodyP"]), Paragraph("<b>Sample ID:</b> BLK-NAG-2026-302", st["BodyP"])],
        [Paragraph("<b>Location:</b> Nagpur, Vidarbha", st["BodyP"]), Paragraph("<b>Soil Type:</b> Black Soil (Deep Regur)", st["BodyP"])],
    ]
    t_meta = Table(meta_data, colWidths=[260, 260])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fbe9e7")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#ffab91")),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    params_data = [
        [Paragraph("Key Variable", st["Th"]), Paragraph("Measured Value", st["Th"]), Paragraph("Unit", st["Th"]), Paragraph("Diagnostic Remark", st["Th"])],
        [Paragraph("Soil pH", st["Td"]), Paragraph("8.1", st["Td"]), Paragraph("scale", st["Td"]), Paragraph("Alkaline (Needs Gypsum)", st["Td"])],
        [Paragraph("Nitrogen (N)", st["Td"]), Paragraph("42.0", st["Td"]), Paragraph("kg/ha", st["Td"]), Paragraph("Deficient", st["Td"])],
        [Paragraph("Phosphorus (P)", st["Td"]), Paragraph("28.0", st["Td"]), Paragraph("kg/ha", st["Td"]), Paragraph("Low-Medium", st["Td"])],
        [Paragraph("Potassium (K)", st["Td"]), Paragraph("85.0", st["Td"]), Paragraph("kg/ha", st["Td"]), Paragraph("Rich / Abundant", st["Td"])],
        [Paragraph("Temperature", st["Td"]), Paragraph("32.5", st["Td"]), Paragraph("°C", st["Td"]), Paragraph("High Heat", st["Td"])],
        [Paragraph("Humidity", st["Td"]), Paragraph("55.0", st["Td"]), Paragraph("%", st["Td"]), Paragraph("Sub-humid", st["Td"])],
        [Paragraph("Rainfall", st["Td"]), Paragraph("85.0", st["Td"]), Paragraph("mm", st["Td"]), Paragraph("Low Rainfall Zone", st["Td"])],
    ]
    t_params = Table(params_data, colWidths=[160, 100, 110, 150])
    t_params.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d84315")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ffccbc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fff3e0")]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_params)

    doc.build(story)
    return filepath


def create_csv_report():
    filepath = os.path.join(SAMPLE_DIR, "sample_field_data.csv")
    content = """parameter,value,unit,rating
ph,6.9,-,Optimal
nitrogen,68.0,kg/ha,Medium
phosphorus,46.0,kg/ha,Medium
potassium,52.0,kg/ha,High
temperature,25.8,C,Normal
humidity,74.0,%,Adequate
rainfall,118.0,mm,Moderate
soil_type,Loamy Soil,-,Medium Texture
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def generate_all():
    print("Generating sample reports in:", SAMPLE_DIR)
    p1 = create_soil_health_card()
    p2 = create_lab_report()
    p3 = create_alkaline_report()
    p4 = create_csv_report()
    print("Created:", [p1, p2, p3, p4])


if __name__ == "__main__":
    generate_all()
