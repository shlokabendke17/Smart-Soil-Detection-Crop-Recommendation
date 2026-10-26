"""
soil_health.py
Computes a 0-100 Soil Health Score from pH and NPK values.
Provides detailed soil parameter breakdown (Nitrogen, Phosphorus, Potassium, pH, Moisture)
with normal agronomic reference ranges, status evaluations (Deficient, Low, Optimal, High, Excess),
and agronomic interpretation for research analysis.

Weights:
    pH balance   : 25 points
    Nitrogen     : 25 points
    Phosphorus   : 25 points
    Potassium    : 25 points
"""

# Agronomic "ideal" ranges (generic, for typical field crops)
PH_IDEAL_MIN, PH_IDEAL_MAX = 6.0, 7.5
N_IDEAL_MIN, N_IDEAL_MAX = 50.0, 100.0     # kg/ha equivalent, dataset-consistent scale
P_IDEAL_MIN, P_IDEAL_MAX = 30.0, 60.0
K_IDEAL_MIN, K_IDEAL_MAX = 30.0, 60.0

# Agronomic reference ranges (generic benchmark for standard agricultural soils)
REFERENCE_RANGES = {
    "ph": {
        "name": "Soil pH",
        "unit": "pH (0-14)",
        "optimal_min": 6.0,
        "optimal_max": 7.5,
        "absolute_min": 3.5,
        "absolute_max": 9.5,
        "low_threshold": 5.5,
        "high_threshold": 8.0,
        "agronomic_role": "Controls nutrient bioavailability and root cellular uptake capacity.",
    },
    "nitrogen": {
        "name": "Nitrogen (N)",
        "unit": "kg/ha",
        "optimal_min": 50.0,
        "optimal_max": 100.0,
        "absolute_min": 0.0,
        "absolute_max": 140.0,
        "low_threshold": 40.0,
        "high_threshold": 110.0,
        "agronomic_role": "Primary driver of chlorophyll synthesis, foliar canopy growth, and protein metabolism.",
    },
    "phosphorus": {
        "name": "Phosphorus (P)",
        "unit": "kg/ha",
        "optimal_min": 30.0,
        "optimal_max": 60.0,
        "absolute_min": 0.0,
        "absolute_max": 145.0,
        "low_threshold": 25.0,
        "high_threshold": 75.0,
        "agronomic_role": "Drives early root elongation, cellular energy transfer (ATP), and flower/seed setting.",
    },
    "potassium": {
        "name": "Potassium (K)",
        "unit": "kg/ha",
        "optimal_min": 30.0,
        "optimal_max": 60.0,
        "absolute_min": 0.0,
        "absolute_max": 205.0,
        "low_threshold": 25.0,
        "high_threshold": 80.0,
        "agronomic_role": "Regulates stomatal conductance, water stress tolerance, and disease resistance.",
    },
    "moisture": {
        "name": "Moisture / Humidity",
        "unit": "%",
        "optimal_min": 50.0,
        "optimal_max": 75.0,
        "absolute_min": 10.0,
        "absolute_max": 100.0,
        "low_threshold": 40.0,
        "high_threshold": 85.0,
        "agronomic_role": "Facilitates nutrient transport in soil solution and root respiration.",
    }
}


def _evaluate_param_status(value: float, param_key: str) -> dict:
    """Classifies a parameter value against agronomic benchmarks and computes score & deviation."""
    ref = REFERENCE_RANGES[param_key]
    opt_min, opt_max = ref["optimal_min"], ref["optimal_max"]
    abs_min, abs_max = ref["absolute_min"], ref["absolute_max"]
    low_th, high_th = ref["low_threshold"], ref["high_threshold"]

    # Calculate status
    if opt_min <= value <= opt_max:
        status = "Optimal"
        status_code = "optimal"
        status_text = "Within ideal agronomic range"
    elif value < low_th:
        status = "Deficient" if value < (low_th * 0.7) else "Low"
        status_code = "low"
        status_text = f"Deficient ({-round((opt_min - value), 1)} {ref['unit']} below ideal)"
    elif value < opt_min:
        status = "Slightly Low"
        status_code = "low"
        status_text = f"Slightly low ({-round((opt_min - value), 1)} {ref['unit']} below ideal)"
    elif value > high_th:
        status = "Excessive"
        status_code = "excess"
        status_text = f"Excessive (+{round((value - opt_max), 1)} {ref['unit']} above ideal)"
    else:
        status = "Slightly High"
        status_code = "high"
        status_text = f"Slightly high (+{round((value - opt_max), 1)} {ref['unit']} above ideal)"

    # Score component out of 25
    if opt_min <= value <= opt_max:
        score = 25.0
    elif value < opt_min:
        span = max(opt_min - abs_min, 1e-6)
        deficit = min(opt_min - value, span)
        score = max(0.0, 25.0 * (1 - deficit / span))
    else:
        span = max(abs_max - opt_max, 1e-6)
        excess = min(value - opt_max, span)
        score = max(0.0, 25.0 * (1 - excess / span))

    # Normalized percentage against max scale for visual UI gauges (0-100%)
    norm_pct = min(100.0, max(0.0, ((value - abs_min) / (abs_max - abs_min)) * 100.0))

    return {
        "name": ref["name"],
        "key": param_key,
        "value": round(float(value), 1),
        "unit": ref["unit"],
        "score": round(score, 1),
        "score_max": 25,
        "status": status,
        "status_code": status_code,
        "status_text": status_text,
        "normal_range": f"{opt_min} – {opt_max} {ref['unit']}",
        "normal_min": opt_min,
        "normal_max": opt_max,
        "gauge_pct": round(norm_pct, 1),
        "role": ref["agronomic_role"],
    }


def compute_soil_health(ph: float, n: float, p: float, k: float, moisture: float = None) -> dict:
    """
    Returns comprehensive soil health calculation:
    - Overall 0-100 score & classification
    - Detailed parameter breakdown for pH, Nitrogen, Phosphorus, Potassium (and optional Moisture)
    - Normal vs Actual metrics for research comparison
    """
    ph_data = _evaluate_param_status(ph, "ph")
    n_data  = _evaluate_param_status(n, "nitrogen")
    p_data  = _evaluate_param_status(p, "phosphorus")
    k_data  = _evaluate_param_status(k, "potassium")

    total_score = round(ph_data["score"] + n_data["score"] + p_data["score"] + k_data["score"])

    if total_score >= 80:
        level = "Excellent"
        summary = "Optimal nutrient profile and biochemical equilibrium supporting high yield potential."
    elif total_score >= 60:
        level = "Good"
        summary = "Favorable soil condition with minor nutrient adjustments recommended for maximum yield."
    elif total_score >= 40:
        level = "Moderate"
        summary = "Imbalanced nutrient profile requiring targeted fertilizer amendments to prevent yield losses."
    else:
        level = "Poor"
        summary = "Significant nutrient deficiencies or pH stress present. Immediate corrective action required."

    breakdown = {
        "ph": ph_data["score"],
        "nitrogen": n_data["score"],
        "phosphorus": p_data["score"],
        "potassium": k_data["score"],
    }

    parameters = [ph_data, n_data, p_data, k_data]
    if moisture is not None:
        m_data = _evaluate_param_status(moisture, "moisture")
        parameters.append(m_data)

    return {
        "score": total_score,
        "level": level,
        "summary": summary,
        "breakdown": breakdown,
        "parameters": parameters,
        "parameter_dict": {
            "ph": ph_data,
            "nitrogen": n_data,
            "phosphorus": p_data,
            "potassium": k_data,
            **({"moisture": _evaluate_param_status(moisture, "moisture")} if moisture is not None else {})
        }
    }
