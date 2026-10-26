import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Locate dataset whether run from root or project/backend
possible_paths = [
    "Crop_recommendation.csv",
    "crop_recommendation.csv",
    os.path.join("..", "..", "Crop_recommendation.csv"),
    os.path.join("..", "Crop_recommendation.csv"),
    os.path.join(os.path.dirname(__file__), "Crop_recommendation.csv"),
    os.path.join(os.path.dirname(__file__), "..", "..", "Crop_recommendation.csv"),
]

data_path = None
for p in possible_paths:
    if os.path.exists(p):
        data_path = p
        break

if not data_path:
    raise FileNotFoundError("Could not find Crop_recommendation.csv. Ensure it is in the project folder.")

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET = "label"

df = pd.read_csv(data_path)
required = FEATURES + [TARGET]

# Check columns
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns: {missing}. Found: {list(df.columns)}")

df = df[required].dropna()
X = df[FEATURES]
y = df[TARGET]

# Stratified split 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

# Train model
model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
model.fit(X_train, y_train)

# Predictions & Metrics
pred = model.predict(X_test)

print("=" * 65)
print("             MODEL EVALUATION TERMINAL OUTPUT")
print("=" * 65)
print("Test accuracy:", round(accuracy_score(y_test, pred), 4))
print("\nClassification report:\n")
print(classification_report(y_test, pred))
print("Confusion matrix:\n")
print(confusion_matrix(y_test, pred))
print("=" * 65)

joblib.dump({"model": model, "features": FEATURES}, "crop_model.joblib")
print("Saved model to crop_model.joblib")
