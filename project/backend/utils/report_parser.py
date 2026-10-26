"""
report_parser.py
Extracts soil chemical composition (pH, N, P, K) and agro-climatic variables
(temperature, humidity, rainfall) from uploaded soil test reports.

Supported formats:
  - PDF files (Soil Health Cards, laboratory analysis reports, previous system PDFs)
  - CSV / TSV spreadsheets
  - Plaintext (.txt, .log)
  - Scanned/camera images (.jpg, .jpeg, .png, .webp)
"""

import os
import io
import re
import csv
import json
from datetime import datetime

# PDF extraction
try:
    import pypdf
    _PYPDF_AVAILABLE = True
except ImportError:
    _PYPDF_AVAILABLE = False

# Image handling
try:
    from PIL import Image
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False


# ── Known Soil Types for entity recognition ─────────────────────────────────
KNOWN_SOIL_TYPES = [
    ("black soil", "Black Soil"),
    ("black cotton", "Black Soil"),
    ("regur", "Black Soil"),
    ("clayey loam", "Clay Loam"),
    ("clay loam", "Clay Loam"),
    ("sandy loam", "Sandy Loam"),
    ("silt loam", "Silt Loam"),
    ("loamy soil", "Loamy Soil"),
    ("loam", "Loamy Soil"),
    ("clay soil", "Clay Soil"),
    ("clay", "Clay Soil"),
    ("sandy soil", "Sandy Soil"),
    ("sand", "Sandy Soil"),
    ("red soil", "Red Soil"),
    ("alluvial soil", "Alluvial Soil"),
    ("alluvial", "Alluvial Soil"),
    ("laterite soil", "Laterite Soil"),
    ("laterite", "Laterite Soil"),
]


def _clean_num(val_str: str) -> float | None:
    """Helper to convert cleaned numeric substring to float."""
    if not val_str:
        return None
    val_str = val_str.strip().replace(",", ".")
    # Remove trailing non-digit chars
    m = re.match(r"^[-+]?[0-9]+(?:\.[0-9]+)?", val_str)
    if m:
        try:
            return float(m.group(0))
        except (ValueError, TypeError):
            return None
    return None


def extract_parameters_from_text(raw_text: str) -> dict:
    """
    Intelligent multi-strategy parser that searches for agronomic parameters
    in unstructured, tabular, or key-value text.
    """
    extracted = {}
    confidence = {}
    metadata = {}

    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

    # ──────────────────────────────────────────────────────────────────────────
    # STRATEGY 1: ReportLab Columnar Tables (as in system-generated PDF exports)
    # ──────────────────────────────────────────────────────────────────────────
    for i, line in enumerate(lines):
        # Match Soil Parameters block:
        # Soil Parameters
        #  pH
        # Nitrogen (N)
        # Phosphorus (P)
        # Potassium (K)
        # 6.5
        # 65
        # 48
        # 45
        if re.search(r"\bsoil\s+parameters?\b", line, re.I):
            sub = lines[i+1 : min(len(lines), i+15)]
            nums = []
            for item in sub:
                val = _clean_num(item)
                if val is not None and re.match(r"^[-+]?[0-9]+(?:\.[0-9]+)?$", item):
                    nums.append(val)
                elif "weather" in item.lower() or "health" in item.lower():
                    break
            if len(nums) >= 4:
                extracted["ph"] = nums[0]
                extracted["n"] = nums[1]
                extracted["p"] = nums[2]
                extracted["k"] = nums[3]
                confidence["ph"] = "high"
                confidence["n"] = "high"
                confidence["p"] = "high"
                confidence["k"] = "high"

        # Match Weather Conditions block:
        # Weather Conditions
        #  Temperature (°C)
        # Humidity (%)
        # Rainfall (mm)
        # 26.5
        # 72
        # 110
        if re.search(r"\bweather\s+conditions?\b|\bagro[- ]climatic\b", line, re.I):
            sub = lines[i+1 : min(len(lines), i+12)]
            nums = []
            for item in sub:
                val = _clean_num(item)
                if val is not None and re.match(r"^[-+]?[0-9]+(?:\.[0-9]+)?$", item):
                    nums.append(val)
                elif "score" in item.lower() or "crop" in item.lower():
                    break
            if len(nums) >= 3:
                extracted["temperature"] = nums[0]
                extracted["humidity"] = nums[1]
                extracted["rainfall"] = nums[2]
                confidence["temperature"] = "high"
                confidence["humidity"] = "high"
                confidence["rainfall"] = "high"

    # ──────────────────────────────────────────────────────────────────────────
    # STRATEGY 2: Key-Value and Delimited Line Patterns
    # (Matches Soil Health Cards, Lab Reports, Inline entries)
    # ──────────────────────────────────────────────────────────────────────────

    # 1. Soil pH (0 - 14)
    if "ph" not in extracted:
        # Matches: pH: 6.5, Soil pH = 7.2, Reaction (pH): 6.8, pH (1:2.5 w/v) : 6.8, pH (H2O): 6.5
        m = re.search(
            r"(?:soil\s*(?:reaction|test)?\s*)?(?:\bpH\b|\(pH\))"
            r"(?:\s*\([^)]*\))?"
            r"[\s:=|\-–]+([0-9]+(?:\.[0-9]+)?)",
            raw_text,
            re.IGNORECASE,
        )
        if m:
            val = _clean_num(m.group(1))
            if val is not None and 0.0 <= val <= 14.0:
                extracted["ph"] = round(val, 2)
                confidence["ph"] = "high"

    # 2. Nitrogen (N)
    if "n" not in extracted:
        m = re.search(
            r"(?:available\s*)?(?:\bnitrogen\b|\bavail(?:\.|\s+)n\b|nitrogen\s*\(N\))"
            r"(?:\s*\([^)]+\))?"
            r"[\s:=|\-–]+([0-9]+(?:\.[0-9]+)?)",
            raw_text,
            re.IGNORECASE,
        )
        if m:
            val = _clean_num(m.group(1))
            if val is not None:
                extracted["n"] = round(val, 1)
                confidence["n"] = "high"
        else:
            # Short form: N: 65 or N (kg/ha): 65
            m_short = re.search(r"\bN\s*(?:\([^)]*\)|kg/ha)?[\s:=|\-–]+([0-9]+(?:\.[0-9]+)?)", raw_text)
            if m_short:
                val = _clean_num(m_short.group(1))
                if val is not None and 0 <= val <= 350:
                    extracted["n"] = round(val, 1)
                    confidence["n"] = "medium"

    # 3. Phosphorus (P)
    if "p" not in extracted:
        m = re.search(
            r"(?:available\s*)?(?:\bphosphorus\b|\bphosphate\b|\bavail(?:\.|\s+)p\b|phosphorus\s*\(P\)|P2O5)"
            r"(?:\s*\([^)]+\))?"
            r"[\s:=|\-–]+([0-9]+(?:\.[0-9]+)?)",
            raw_text,
            re.IGNORECASE,
        )
        if m:
            val = _clean_num(m.group(1))
            if val is not None:
                extracted["p"] = round(val, 1)
                confidence["p"] = "high"
        else:
            # Short form: P: 48 or P (kg/ha): 48
            m_short = re.search(r"\bP\s*(?:\([^)]*\)|kg/ha)?[\s:=|\-–]+([0-9]+(?:\.[0-9]+)?)", raw_text)
            if m_short:
                val = _clean_num(m_short.group(1))
                if val is not None and 0 <= val <= 250:
                    extracted["p"] = round(val, 1)
                    confidence["p"] = "medium"

    # 4. Potassium (K)
    if "k" not in extracted:
        m = re.search(
            r"(?:available\s*)?(?:\bpotassium\b|\bpotash\b|\bavail(?:\.|\s+)k\b|potassium\s*\(K\)|K2O)"
            r"(?:\s*\([^)]+\))?"
            r"[\s:=|\-–]+([0-9]+(?:\.[0-9]+)?)",
            raw_text,
            re.IGNORECASE,
        )
        if m:
            val = _clean_num(m.group(1))
            if val is not None:
                extracted["k"] = round(val, 1)
                confidence["k"] = "high"
        else:
            # Short form: K: 45 or K (kg/ha): 45
            m_short = re.search(r"\bK\s*(?:\([^)]*\)|kg/ha)?[\s:=|\-–]+([0-9]+(?:\.[0-9]+)?)", raw_text)
            if m_short:
                val = _clean_num(m_short.group(1))
                if val is not None and 0 <= val <= 350:
                    extracted["k"] = round(val, 1)
                    confidence["k"] = "medium"

    # 5. Temperature (°C)
    if "temperature" not in extracted:
        m = re.search(
            r"(?:ambient\s*|air\s*|mean\s*)?(?:temp(?:erature)?)"
            r"(?:\s*\([^)]*\))?"
            r"[\s:=|\-–]+([0-9]+(?:\.[0-9]+)?)",
            raw_text,
            re.IGNORECASE,
        )
        if m:
            val = _clean_num(m.group(1))
            if val is not None and -10.0 <= val <= 55.0:
                extracted["temperature"] = round(val, 1)
                confidence["temperature"] = "high"
        else:
            # Check for patterns like "26.5 °C" or "26.5°C"
            m_deg = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*°\s*C\b", raw_text, re.IGNORECASE)
            if m_deg:
                val = _clean_num(m_deg.group(1))
                if val is not None and -10.0 <= val <= 55.0:
                    extracted["temperature"] = round(val, 1)
                    confidence["temperature"] = "medium"

    # 6. Humidity / Moisture (%)
    if "humidity" not in extracted:
        m = re.search(
            r"(?:relative\s*)?(?:humidity|moisture(?:\s*content)?|\bRH\b)"
            r"(?:\s*\([^)]*\))?"
            r"[\s:=|\-–]+([0-9]+(?:\.[0-9]+)?)",
            raw_text,
            re.IGNORECASE,
        )
        if m:
            val = _clean_num(m.group(1))
            if val is not None and 0.0 <= val <= 100.0:
                extracted["humidity"] = round(val, 1)
                confidence["humidity"] = "high"

    # 7. Rainfall / Precipitation (mm)
    if "rainfall" not in extracted:
        m = re.search(
            r"(?:annual\s*|monsoon\s*|seasonal\s*|expected\s*)?(?:precipitation|rainfall|rain)"
            r"(?:\s*\([^)]*\))?"
            r"[\s:=|\-–]+([0-9]+(?:\.[0-9]+)?)",
            raw_text,
            re.IGNORECASE,
        )
        if m:
            val = _clean_num(m.group(1))
            if val is not None and 0.0 <= val <= 1500.0:
                extracted["rainfall"] = round(val, 1)
                confidence["rainfall"] = "high"
        else:
            m_mm = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*mm\s*(?:rain|precipitation|rainfall)?", raw_text, re.IGNORECASE)
            if m_mm:
                val = _clean_num(m_mm.group(1))
                if val is not None and 0.0 <= val <= 1500.0:
                    extracted["rainfall"] = round(val, 1)
                    confidence["rainfall"] = "medium"

    # ──────────────────────────────────────────────────────────────────────────
    # STRATEGY 3: Soil Type & Agronomic Metadata Detection
    # ──────────────────────────────────────────────────────────────────────────
    text_lower = raw_text.lower()
    for needle, formal_name in KNOWN_SOIL_TYPES:
        if needle in text_lower:
            metadata["soil_type"] = formal_name
            break

    # Organic Carbon (OC)
    m_oc = re.search(
        r"(?:organic\s*carbon|\bOC\b)(?:\s*\([^)]*\))?[\s:=|\-–]+([0-9]+(?:\.[0-9]+)?)",
        raw_text,
        re.IGNORECASE,
    )
    if m_oc:
        val = _clean_num(m_oc.group(1))
        if val is not None:
            metadata["organic_carbon"] = val

    # Electrical Conductivity (EC)
    m_ec = re.search(
        r"(?:electrical\s*conductivity|\bEC\b)(?:\s*\([^)]*\))?[\s:=|\-–]+([0-9]+(?:\.[0-9]+)?)",
        raw_text,
        re.IGNORECASE,
    )
    if m_ec:
        val = _clean_num(m_ec.group(1))
        if val is not None:
            metadata["electrical_conductivity"] = val

    # Sample ID / Card No
    m_id = re.search(
        r"(?:sample\s*(?:id|no|number)|card\s*no|report\s*id)[\s:=|\-–]+([A-Z0-9\-_/]+)",
        raw_text,
        re.IGNORECASE,
    )
    if m_id:
        metadata["sample_id"] = m_id.group(1).strip()

    # Farmer / Client Name
    m_farmer = re.search(
        r"(?:farmer(?:\s*name)?|client|owner|grower)[\s:=|\-–]+([A-Za-z\s\.\-_]+)(?:\n|$)",
        raw_text,
        re.IGNORECASE,
    )
    if m_farmer:
        name = m_farmer.group(1).strip()
        if len(name) > 2 and len(name) < 40:
            metadata["farmer_name"] = name

    # District / Location
    m_loc = re.search(
        r"(?:district|location|field\s*location|village|taluka)[\s:=|\-–]+([A-Za-z0-9\s,\.\-_]+)(?:\n|$)",
        raw_text,
        re.IGNORECASE,
    )
    if m_loc:
        loc = m_loc.group(1).strip()
        if len(loc) > 2 and len(loc) < 50:
            metadata["location"] = loc

    return {
        "extracted": extracted,
        "confidence": confidence,
        "metadata": metadata,
    }


def parse_csv_or_tsv(content: str) -> dict:
    """Extract soil parameters from a CSV or TSV string."""
    raw_text = content
    extracted = {}
    confidence = {}
    metadata = {}

    try:
        reader = csv.reader(io.StringIO(content))
        for row in reader:
            if len(row) >= 2:
                key = row[0].strip().lower()
                val = _clean_num(row[1])
                if val is None:
                    continue
                if key == "ph" or key.startswith("ph ") or key.startswith("ph(") or "soil ph" in key or "soil reaction" in key:
                    extracted["ph"] = val
                    confidence["ph"] = "high"
                elif "nitrogen" in key or key == "n":
                    extracted["n"] = val
                    confidence["n"] = "high"
                elif "phosphorus" in key or key == "p" or "p2o5" in key:
                    extracted["p"] = val
                    confidence["p"] = "high"
                elif "potassium" in key or key == "k" or "k2o" in key:
                    extracted["k"] = val
                    confidence["k"] = "high"
                elif "temp" in key:
                    extracted["temperature"] = val
                    confidence["temperature"] = "high"
                elif "humid" in key or "moist" in key:
                    extracted["humidity"] = val
                    confidence["humidity"] = "high"
                elif "rain" in key or "precip" in key:
                    extracted["rainfall"] = val
                    confidence["rainfall"] = "high"
    except Exception:
        pass

    # Also run text parser over the full text to catch anything missed
    text_res = extract_parameters_from_text(raw_text)
    for k, v in text_res["extracted"].items():
        extracted.setdefault(k, v)
    for k, v in text_res["confidence"].items():
        confidence.setdefault(k, v)
    metadata.update(text_res["metadata"])

    return {"extracted": extracted, "confidence": confidence, "metadata": metadata}


def parse_pdf_bytes(pdf_bytes: bytes) -> dict:
    """Extract text and parameters from PDF bytes using pypdf."""
    if not _PYPDF_AVAILABLE:
        raise RuntimeError("pypdf is required to parse PDF soil test reports.")

    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    num_pages = len(reader.pages)
    text_parts = []

    for page in reader.pages:
        try:
            pt = page.extract_text()
            if pt:
                text_parts.append(pt)
        except Exception:
            pass

    full_text = "\n".join(text_parts)
    result = extract_parameters_from_text(full_text)
    result["raw_text_snippet"] = full_text[:800] if full_text else "No extractable text found in PDF."
    result["num_pages"] = num_pages
    return result


def parse_report_file(
    file_bytes: bytes,
    filename: str = "report.pdf"
) -> dict:
    """
    Main entry point: parses any soil test report file (PDF, CSV, TXT, Image).
    Returns a unified response dictionary with extracted parameters,
    confidence ratings, metadata, and user-friendly summary.
    """
    ext = os.path.splitext(filename.lower())[1]
    file_type = "unknown"
    parsed_info = {"extracted": {}, "confidence": {}, "metadata": {}}
    raw_snippet = ""

    if ext == ".pdf":
        file_type = "pdf"
        parsed_info = parse_pdf_bytes(file_bytes)
        raw_snippet = parsed_info.get("raw_text_snippet", "")

    elif ext in [".csv", ".tsv", ".txt"]:
        file_type = "csv" if ext in [".csv", ".tsv"] else "text"
        try:
            content = file_bytes.decode("utf-8", errors="replace")
        except Exception:
            content = file_bytes.decode("latin-1", errors="replace")
        parsed_info = parse_csv_or_tsv(content)
        raw_snippet = content[:800]

    elif ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]:
        file_type = "image"
        # Check if EasyOCR is available and models are ready
        ocr_text = ""
        try:
            import easyocr
            reader = easyocr.Reader(["en"], gpu=False, verbose=False)
            results = reader.readtext(file_bytes)
            ocr_text = "\n".join([r[1] for r in results])
        except Exception as ocr_err:
            # If easyocr fails or is downloading, check PIL metadata
            if _PIL_AVAILABLE:
                try:
                    img = Image.open(io.BytesIO(file_bytes))
                    # check for image info / comments
                    ocr_text = str(img.info)
                except Exception:
                    pass

        if ocr_text:
            parsed_info = extract_parameters_from_text(ocr_text)
            raw_snippet = ocr_text[:800]
        else:
            raw_snippet = "Image received. Optical Character Recognition (OCR) processed image features."
            # If image didn't yield text, provide default or metadata if present
            parsed_info = {"extracted": {}, "confidence": {}, "metadata": {}}

    else:
        # Fallback text attempt
        try:
            content = file_bytes.decode("utf-8", errors="replace")
            parsed_info = extract_parameters_from_text(content)
            raw_snippet = content[:800]
            file_type = "text"
        except Exception:
            file_type = "binary"

    extracted = parsed_info.get("extracted", {})
    confidence = parsed_info.get("confidence", {})
    metadata = parsed_info.get("metadata", {})

    # Generate human-readable summary
    found_parts = []
    if "ph" in extracted:
        found_parts.append(f"pH ({extracted['ph']})")
    if "n" in extracted:
        found_parts.append(f"Nitrogen ({extracted['n']} kg/ha)")
    if "p" in extracted:
        found_parts.append(f"Phosphorus ({extracted['p']} kg/ha)")
    if "k" in extracted:
        found_parts.append(f"Potassium ({extracted['k']} kg/ha)")
    if "temperature" in extracted:
        found_parts.append(f"Temp ({extracted['temperature']} °C)")
    if "humidity" in extracted:
        found_parts.append(f"Humidity ({extracted['humidity']} %)")
    if "rainfall" in extracted:
        found_parts.append(f"Rainfall ({extracted['rainfall']} mm)")

    count = len(found_parts)
    if count > 0:
        summary_msg = f"Successfully extracted {count} agronomic parameters from {filename}: " + ", ".join(found_parts)
    else:
        summary_msg = f"Could not detect standard soil parameters in {filename}. Please ensure the report contains labeled pH, N, P, K, or weather values."

    return {
        "success": count > 0,
        "filename": filename,
        "file_type": file_type,
        "extracted_data": extracted,
        "confidence": confidence,
        "metadata": metadata,
        "detected_count": count,
        "summary": summary_msg,
        "raw_snippet": raw_snippet,
    }
