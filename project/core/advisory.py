"""
advisory.py
Rule-based Fertilizer Suggestion (from NPK deficiency) and Nutrient/Soil
Improvement Advisory.

IMPORTANT: These functions consume ONLY numeric soil parameters (pH, N, P, K)
and weather data. They never take the CNN image-classification result as
input, per the system's core design rule.
"""

from .soil_health import N_IDEAL_MIN, N_IDEAL_MAX, P_IDEAL_MIN, P_IDEAL_MAX, K_IDEAL_MIN, K_IDEAL_MAX


def suggest_fertilizer(n: float, p: float, k: float) -> list:
    """Return a list of {'nutrient','status','fertilizer','reason'} dicts."""
    suggestions = []

    if n < N_IDEAL_MIN:
        suggestions.append({
            "nutrient": "Nitrogen",
            "status": "Low",
            "fertilizer": "Urea (46-0-0)",
            "reason": f"N={n} is below the ideal band ({N_IDEAL_MIN}-{N_IDEAL_MAX}).",
        })
    elif n > N_IDEAL_MAX:
        suggestions.append({
            "nutrient": "Nitrogen",
            "status": "High",
            "fertilizer": "Reduce nitrogen input; avoid urea top-dressing",
            "reason": f"N={n} exceeds the ideal band ({N_IDEAL_MIN}-{N_IDEAL_MAX}); risk of lodging/leaching.",
        })

    if p < P_IDEAL_MIN:
        suggestions.append({
            "nutrient": "Phosphorus",
            "status": "Low",
            "fertilizer": "DAP (18-46-0) or Single Super Phosphate",
            "reason": f"P={p} is below the ideal band ({P_IDEAL_MIN}-{P_IDEAL_MAX}).",
        })
    elif p > P_IDEAL_MAX:
        suggestions.append({
            "nutrient": "Phosphorus",
            "status": "High",
            "fertilizer": "Avoid further phosphatic fertilizer this season",
            "reason": f"P={p} exceeds the ideal band ({P_IDEAL_MIN}-{P_IDEAL_MAX}).",
        })

    if k < K_IDEAL_MIN:
        suggestions.append({
            "nutrient": "Potassium",
            "status": "Low",
            "fertilizer": "Muriate of Potash (MOP, 0-0-60)",
            "reason": f"K={k} is below the ideal band ({K_IDEAL_MIN}-{K_IDEAL_MAX}).",
        })
    elif k > K_IDEAL_MAX:
        suggestions.append({
            "nutrient": "Potassium",
            "status": "High",
            "fertilizer": "Avoid further potash application this season",
            "reason": f"K={k} exceeds the ideal band ({K_IDEAL_MIN}-{K_IDEAL_MAX}).",
        })

    if not suggestions:
        suggestions.append({
            "nutrient": "N-P-K",
            "status": "Balanced",
            "fertilizer": "Maintenance dose (balanced NPK, e.g. 19-19-19)",
            "reason": "All major nutrients are within the ideal band.",
        })

    return suggestions


def nutrient_advisory(ph: float, n: float, p: float, k: float) -> list:
    """Return a list of plain-language soil-improvement advice strings."""
    advice = []

    if ph < 5.5:
        advice.append("Soil is acidic — apply agricultural lime to raise pH gradually.")
    elif ph > 8.0:
        advice.append("Soil is alkaline — apply gypsum or elemental sulfur, and add organic matter.")
    elif ph < N_IDEAL_MIN and False:
        pass  # placeholder guard (kept for clarity, no-op)

    if n < N_IDEAL_MIN:
        advice.append("Add well-decomposed compost or farmyard manure (FYM) to boost nitrogen naturally.")
    if p < P_IDEAL_MIN:
        advice.append("Incorporate bone meal or rock phosphate to improve long-term phosphorus availability.")
    if k < K_IDEAL_MIN:
        advice.append("Apply wood ash or potash-rich organic residue to raise potassium levels.")

    if not advice:
        advice.append("Soil nutrient status is healthy — maintain with regular organic matter addition and crop rotation.")

    advice.append("Practice crop rotation and cover cropping to sustain long-term soil structure and microbial health.")
    return advice
