"""
fallback_image_classifier.py
A transparent, non-deep-learning fallback used when PyTorch is unavailable
or weights are loading. It estimates soil type from the average pixel color of the image,
based on well-known soil-color associations.
"""

from PIL import Image

SOIL_CLASSES = ["Sandy", "Clay", "Loamy", "Black", "Red"]

# Soil Profiles & Agronomic Characteristics for Research UI
SOIL_PROFILES = {
    "Sandy": {
        "texture": "Coarse & Gritty",
        "drainage": "Very Fast (Excessive)",
        "nutrient_retention": "Low",
        "description": "High sand particles (>85%), warm and well-aerated but prone to quick nutrient leaching.",
        "best_crops": ["Watermelon", "Muskmelon", "Peanuts", "Potatoes", "Carrots"],
        "recommended_amendment": "Add organic compost, peat moss, or farmyard manure to boost water retention."
    },
    "Clay": {
        "texture": "Fine & Sticky when wet",
        "drainage": "Slow (High water retention)",
        "nutrient_retention": "Very High",
        "description": "Dense particle structure (>40% clay), holds moisture and nutrients well but susceptible to waterlogging.",
        "best_crops": ["Rice", "Wheat", "Sugarcane", "Broccoli", "Cabbage"],
        "recommended_amendment": "Incorporate coarse sand and gypsum or organic mulch to improve aeration and drainage."
    },
    "Loamy": {
        "texture": "Even, crumbly & friable",
        "drainage": "Ideal / Well-balanced",
        "nutrient_retention": "High",
        "description": "The agricultural gold standard (40% sand, 40% silt, 20% clay), optimal balance of drainage and nutrients.",
        "best_crops": ["Cotton", "Sugarcane", "Maize", "Wheat", "Pulses", "Vegetables"],
        "recommended_amendment": "Maintain organic matter levels with regular crop rotation and green manuring."
    },
    "Black": {
        "texture": "Clayey, deep & swelling (Regur)",
        "drainage": "Moderate to Slow",
        "nutrient_retention": "Very High (Rich in Calcium & Magnesia)",
        "description": "Derived from basalt/lava rocks, highly fertile and moisture-retentive, ideal for cash crops.",
        "best_crops": ["Cotton", "Soybean", "Sorghum", "Millets", "Sunflower"],
        "recommended_amendment": "Ensure drainage channels during heavy monsoons to avoid root rot."
    },
    "Red": {
        "texture": "Porous, friable & gravelly",
        "drainage": "Good to Fast",
        "nutrient_retention": "Moderate to Low",
        "description": "High ferric oxide content giving characteristic red hue, generally low in nitrogen and phosphorus.",
        "best_crops": ["Groundnut", "Millets", "Tobacco", "Pulses", "Oilseeds"],
        "recommended_amendment": "Apply balanced NPK fertilizer and bio-fertilizers like Rhizobium and mycorrhizae."
    }
}

# Reference average RGB "fingerprints" for each soil class
REFERENCE_RGB = {
    "Sandy": (194, 178, 128),
    "Clay":  (150, 130, 110),
    "Loamy": (110, 80, 55),
    "Black": (45, 42, 40),
    "Red":   (150, 70, 45),
}


def _avg_rgb(image_path: str):
    img = Image.open(image_path).convert("RGB").resize((64, 64))
    pixels = list(img.getdata())
    n = len(pixels)
    r = sum(p[0] for p in pixels) / n
    g = sum(p[1] for p in pixels) / n
    b = sum(p[2] for p in pixels) / n
    return round(r, 1), round(g, 1), round(b, 1)


def classify_by_color(image_path: str) -> dict:
    r, g, b = _avg_rgb(image_path)

    distances = {}
    for soil, (rr, rg, rb) in REFERENCE_RGB.items():
        distances[soil] = ((r - rr) ** 2 + (g - rg) ** 2 + (b - rb) ** 2) ** 0.5

    best = min(distances, key=distances.get)
    max_d = max(distances.values()) or 1.0
    confidence = max(60.0, min(96.0, 100.0 * (1 - distances[best] / max_d)))

    profile = SOIL_PROFILES.get(best, {})

    return {
        "soil_type": best,
        "confidence": round(confidence, 1),
        "method": "Color Heuristic Spectrum",
        "rgb": {"r": r, "g": g, "b": b},
        "profile": profile
    }
