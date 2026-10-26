"""
fertilizer_model.py
OPTIONAL / SECONDARY fertilizer classifier trained on Fertilizer_Prediction.csv
(Temperature, Humidity, Moisture, Soil Type, Crop Type, N, K, P -> Fertilizer Name).

This is a bonus ML-based cross-check alongside the primary rule-based
NPK-deficiency advisor in core/advisory.py. Note that this dataset's
"Soil Type" column is a categorical field the USER selects/knows (or that a
soil test slip states) — it is intentionally NOT wired to the CNN image
classifier output, to keep the CNN strictly reference-only as required.
"""

import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "..", "data", "Fertilizer_Prediction.csv")
MODEL_PATH = os.path.join(HERE, "fertilizer_model.joblib")
ENCODERS_PATH = os.path.join(HERE, "fertilizer_encoders.joblib")

NUMERIC_FEATURES = ["Temparature", "Humidity ", "Moisture", "Nitrogen", "Potassium", "Phosphorous"]
CAT_FEATURES = ["Soil Type", "Crop Type"]

VALID_SOIL_TYPES = ["Sandy", "Loamy", "Black", "Red", "Clayey"]
VALID_CROP_TYPES = ["Maize", "Sugarcane", "Cotton", "Tobacco", "Paddy", "Barley",
                     "Wheat", "Millets", "Oil seeds", "Pulses", "Ground Nuts"]


def train(save: bool = True) -> dict:
    df = pd.read_csv(DATA_PATH)
    df.columns = [c.strip() if c.strip() != "Humidity" else "Humidity " for c in df.columns]

    encoders = {}
    for col in CAT_FEATURES:
        le = LabelEncoder()
        df[col + "_enc"] = le.fit_transform(df[col])
        encoders[col] = le

    feature_cols = NUMERIC_FEATURES + [c + "_enc" for c in CAT_FEATURES]
    X = df[feature_cols]
    y = df["Fertilizer Name"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    clf = RandomForestClassifier(n_estimators=200, random_state=42)
    clf.fit(X_train, y_train)
    acc = accuracy_score(y_test, clf.predict(X_test))

    if save:
        joblib.dump(clf, MODEL_PATH)
        joblib.dump(encoders, ENCODERS_PATH)

    return {"model": clf, "encoders": encoders, "test_accuracy": acc}


def load_model():
    if not (os.path.exists(MODEL_PATH) and os.path.exists(ENCODERS_PATH)):
        result = train(save=True)
        return result["model"], result["encoders"]
    return joblib.load(MODEL_PATH), joblib.load(ENCODERS_PATH)


def predict_fertilizer_ml(temperature: float, humidity: float, moisture: float,
                           soil_type: str, crop_type: str,
                           n: float, k: float, p: float) -> str:
    """Secondary ML cross-check. soil_type/crop_type must come from user input
    or the crop-recommendation output — never from the CNN image classifier."""
    clf, encoders = load_model()

    if soil_type not in encoders["Soil Type"].classes_:
        soil_type = min(VALID_SOIL_TYPES, key=lambda s: 0)  # fallback default
        soil_type = encoders["Soil Type"].classes_[0]
    if crop_type not in encoders["Crop Type"].classes_:
        crop_type = encoders["Crop Type"].classes_[0]

    soil_enc = encoders["Soil Type"].transform([soil_type])[0]
    crop_enc = encoders["Crop Type"].transform([crop_type])[0]

    row = pd.DataFrame([{
        "Temparature": temperature, "Humidity ": humidity, "Moisture": moisture,
        "Nitrogen": n, "Potassium": k, "Phosphorous": p,
        "Soil Type_enc": soil_enc, "Crop Type_enc": crop_enc,
    }])[NUMERIC_FEATURES + ["Soil Type_enc", "Crop Type_enc"]]

    return clf.predict(row)[0]


if __name__ == "__main__":
    info = train()
    print(f"Fertilizer model trained. Test accuracy: {info['test_accuracy']:.4f}")
