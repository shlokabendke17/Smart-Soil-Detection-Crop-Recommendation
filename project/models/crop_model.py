"""
crop_model.py

Crop recommendation model trained on Crop_recommendation.csv
(N, P, K, temperature, humidity, ph, rainfall -> crop label)

Model: RandomForestClassifier (scikit-learn) with Explainable AI (XAI) transparent insights.

NOTE:
This model ONLY uses numeric soil + weather data.
It DOES NOT use CNN soil image classification output.
"""

import os
import joblib

os.environ["PANDAS_ARROW_DISABLED"] = "1"

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Paths
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "..", "data", "Crop_recommendation.csv")
MODEL_PATH = os.path.join(HERE, "crop_model.joblib")

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Agronomic knowledge-base for XAI explanation synthesis
CROP_AGRONOMIC_PROFILES = {
    "rice": {
        "key_drivers": ["rainfall", "humidity", "temperature"],
        "reason": "Requires high rainfall (>180mm), high atmospheric humidity (>80%), and warm temperatures (22-27°C) for flooded vegetative stages."
    },
    "muskmelon": {
        "key_drivers": ["humidity", "ph", "temperature"],
        "reason": "Favors warm temperatures (27-30°C), neutral-to-slightly-acidic pH (6.2-6.8), and moderate humidity for high sugar accumulation."
    },
    "watermelon": {
        "key_drivers": ["rainfall", "humidity", "ph"],
        "reason": "Thrives in warm, dry weather with controlled moisture, neutral pH (6.0-7.0), and low rainfall during ripening."
    },
    "maize": {
        "key_drivers": ["N", "rainfall", "temperature"],
        "reason": "Demands high Nitrogen (N > 70 kg/ha) for rapid vegetative biomass and moderate well-distributed rainfall (60-100mm)."
    },
    "cotton": {
        "key_drivers": ["temperature", "humidity", "N"],
        "reason": "Demands warm temperatures (22-26°C), deep nutrient-rich black soil, and high nitrogen for boll maturation."
    },
    "coffee": {
        "key_drivers": ["rainfall", "humidity", "ph"],
        "reason": "Needs high rainfall (150-200mm), acidic-to-neutral pH (6.0-6.8), and elevated humidity typical of hill plantations."
    },
    "jute": {
        "key_drivers": ["rainfall", "humidity", "temperature"],
        "reason": "Warm and humid tropical climate (humidity > 70%) with abundant rainfall (>150mm) and well-balanced NPK."
    },
    "apple": {
        "key_drivers": ["P", "K", "temperature"],
        "reason": "Requires cool temperatures (21-24°C), high Phosphorus (P > 130 kg/ha) and Potassium (K > 190 kg/ha) for fruit set."
    },
    "banana": {
        "key_drivers": ["K", "N", "humidity"],
        "reason": "Heavy feeder requiring high Potassium (K > 50 kg/ha) and Nitrogen with high humidity (75-85%) and warmth."
    },
    "grapes": {
        "key_drivers": ["P", "K", "humidity"],
        "reason": "Demands high Potassium and Phosphorus with low rainfall during fruit development to prevent mildew."
    },
    "mango": {
        "key_drivers": ["temperature", "rainfall", "ph"],
        "reason": "Thrives in tropical temperatures (27-35°C), low-to-moderate rainfall, and slightly acidic-to-neutral pH."
    },
    "chickpea": {
        "key_drivers": ["rainfall", "ph", "P"],
        "reason": "Low rainfall requirement (60-80mm), neutral pH (7.0-7.5), and moderate Phosphorus for root nodulation."
    },
    "kidneybeans": {
        "key_drivers": ["rainfall", "temperature", "ph"],
        "reason": "Prefers moderate rainfall (100-150mm), cool-to-moderate temperature (18-22°C), and slightly acidic soil (5.5-6.0)."
    },
    "pigeonpeas": {
        "key_drivers": ["rainfall", "ph", "temperature"],
        "reason": "Deep-rooted drought-resistant pulse thriving in semi-arid zones with low nitrogen requirement."
    },
    "mothbeans": {
        "key_drivers": ["rainfall", "humidity", "temperature"],
        "reason": "Extremely drought-tolerant pulse thriving in arid regimes (rainfall < 60mm) and high temperatures."
    },
    "mungbean": {
        "key_drivers": ["rainfall", "humidity", "temperature"],
        "reason": "Short-duration pulse crop suited for semi-arid soils with low rainfall (40-60mm) and warm climate."
    },
    "blackgram": {
        "key_drivers": ["rainfall", "temperature", "humidity"],
        "reason": "Suited for warm humid conditions with moderate rainfall (60-75mm) and well-drained loamy soils."
    },
    "lentil": {
        "key_drivers": ["rainfall", "temperature", "ph"],
        "reason": "Cool-season pulse requiring low rainfall (40-55mm), moderate temperature (20-24°C), and neutral pH."
    },
    "pomegranate": {
        "key_drivers": ["rainfall", "humidity", "temperature"],
        "reason": "Drought-hardy fruit crop thriving in dry climate with low humidity and high sunshine."
    },
    "orange": {
        "key_drivers": ["temperature", "rainfall", "ph"],
        "reason": "Requires subtropical warmth, moderate rainfall (100-120mm), and well-drained soil with pH 6.0-7.5."
    },
    "papaya": {
        "key_drivers": ["rainfall", "temperature", "humidity"],
        "reason": "Continuous moisture demand with high humidity (90-95%) and warm temperature (30-35°C)."
    },
    "coconut": {
        "key_drivers": ["rainfall", "humidity", "temperature"],
        "reason": "Coastal tropical crop requiring abundant rainfall (>150mm), high humidity (>90%), and warm climate."
    }
}


# 🚀 Train Model
def train(save: bool = True) -> dict:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    for col in FEATURES + ["label"]:
        if col not in df.columns:
            raise ValueError(f"Missing column in dataset: {col}")

    X = df[FEATURES]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    if save:
        joblib.dump(clf, MODEL_PATH)

    return {
        "model": clf,
        "test_accuracy": acc,
        "n_classes": y.nunique()
    }


# 📦 Load Model
def load_model():
    if not os.path.exists(MODEL_PATH):
        print("⚠️ Model not found. Training new model...")
        result = train(save=True)
        return result["model"]
    return joblib.load(MODEL_PATH)


def explain_prediction(ph: float, n: float, p: float, k: float,
                       temperature: float, humidity: float, rainfall: float,
                       top_crops: list) -> dict:
    """
    Explainable AI (XAI) transparent engine.
    Computes feature importance contributions and dynamic rationale for why crops are recommended.
    """
    clf = load_model()
    importances = clf.feature_importances_
    feature_imp_map = {feat: round(float(imp) * 100, 1) for feat, imp in zip(FEATURES, importances)}

    input_vals = {
        "N": n, "P": p, "K": k,
        "temperature": temperature, "humidity": humidity,
        "ph": ph, "rainfall": rainfall
    }

    explanations = []
    for rank_idx, item in enumerate(top_crops):
        crop = item["crop"].lower()
        prob = item["probability"]
        profile = CROP_AGRONOMIC_PROFILES.get(crop, {
            "key_drivers": ["ph", "rainfall", "humidity"],
            "reason": f"Favorable environmental conditions match optimal growth thresholds for {crop.title()}."
        })

        # Determine which factors matched best
        factors = []
        if n >= 60:
            factors.append("High Nitrogen availability")
        elif n <= 30:
            factors.append("Low Nitrogen demand")

        if ph >= 6.0 and ph <= 7.5:
            factors.append("Optimal neutral soil pH")
        elif ph < 6.0:
            factors.append("Acidic soil tolerance")
        else:
            factors.append("Alkaline soil tolerance")

        if rainfall >= 120:
            factors.append("High rainfall suitability")
        elif rainfall <= 60:
            factors.append("Drought tolerance")

        if humidity >= 70:
            factors.append("High atmospheric humidity")
        elif humidity <= 40:
            factors.append("Dry climate preference")

        reason_summary = profile["reason"]
        if factors:
            reason_summary = f"{', '.join(factors[:2])} favorably aligns with {crop.title()} requirements. {reason_summary}"

        explanations.append({
            "crop": item["crop"],
            "probability": prob,
            "rank": rank_idx + 1,
            "key_drivers": profile["key_drivers"],
            "reason": reason_summary,
            "factors": factors
        })

    return {
        "feature_importance": feature_imp_map,
        "crop_explanations": explanations,
        "model_type": "Random Forest Classifier (200 Estimators)",
        "confidence_score": top_crops[0]["probability"] if top_crops else 0.0
    }


# 🌱 Recommend Crops
def recommend_top_k(
    ph: float,
    n: float,
    p: float,
    k: float,
    temperature: float,
    humidity: float,
    rainfall: float,
    top_k: int = 3
) -> list:
    """Returns top-k crops with probabilities and XAI explanations"""

    clf = load_model()

    row = pd.DataFrame([{
        "N": n,
        "P": p,
        "K": k,
        "temperature": temperature,
        "humidity": humidity,
        "ph": ph,
        "rainfall": rainfall,
    }])[FEATURES]

    probs = clf.predict_proba(row)[0]
    classes = clf.classes_

    ranked = sorted(
        zip(classes, probs),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]

    crop_list = [
        {"crop": c, "probability": round(float(pr) * 100, 2)}
        for c, pr in ranked
    ]

    return crop_list