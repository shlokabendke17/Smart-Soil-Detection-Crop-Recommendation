"""
main.py
Orchestrates the full Smart Soil Detection & Crop Recommendation pipeline:

  1. (Optional) CNN image classification of a soil photo  -> reference only
  2. Crop recommendation from pH/NPK + weather              -> RandomForest
  3. Fertilizer suggestion from NPK deficiency               -> rule-based
  4. Soil health score                                       -> rule-based
  5. Nutrient / soil-improvement advisory                    -> rule-based
  6. Risk alerts from weather                                 -> rule-based
  7. AI-generated PDF report                                  -> reportlab

Usage (as a library):
    from main import run_pipeline
    run_pipeline(ph=6.3, n=40, p=45, k=42,
                 temperature=24, humidity=55, rainfall=40,
                 image_path=None, lang="en",
                 output_path="outputs/report.pdf")

Usage (CLI demo):
    python main.py
"""

import os

from models import crop_model
from models import cnn_soil_classifier
from core.soil_health import compute_soil_health
from core.advisory import suggest_fertilizer, nutrient_advisory
from core.risk_alerts import compute_risk_alerts
from report.pdf_report import generate_report


def run_pipeline(ph, n, p, k, temperature, humidity, rainfall,
                  image_path=None, lang="en", output_path="outputs/report.pdf",
                  top_k_crops=3):

    # 1. CNN soil-image classification (reference only, NOT fed downstream)
    cnn_result = None
    if image_path and os.path.exists(image_path):
        cnn_result = cnn_soil_classifier.predict(image_path)

    # 2. Crop recommendation (numeric soil params + weather ONLY)
    crops = crop_model.recommend_top_k(
        ph=ph, n=n, p=p, k=k,
        temperature=temperature, humidity=humidity, rainfall=rainfall,
        top_k=top_k_crops,
    )

    # 3. Fertilizer suggestion (NPK deficiency, rule-based)
    fertilizer = suggest_fertilizer(n, p, k)

    # 4. Soil health score
    health = compute_soil_health(ph, n, p, k)

    # 5. Nutrient / soil-improvement advisory
    advisory = nutrient_advisory(ph, n, p, k)

    # 6. Weather-based risk alerts
    alerts = compute_risk_alerts(temperature, humidity, rainfall)

    # 7. Build PDF report
    payload = {
        "soil_params": {"ph": ph, "n": n, "p": p, "k": k},
        "weather": {"temperature": temperature, "humidity": humidity, "rainfall": rainfall},
        "cnn_result": cnn_result,
        "health": health,
        "crops": crops,
        "fertilizer": fertilizer,
        "advisory": advisory,
        "alerts": alerts,
    }

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    generate_report(output_path, lang, payload)

    return payload


if __name__ == "__main__":
    # Demo run mirroring the "Expected Output Example" from the spec
    result = run_pipeline(
        ph=6.3, n=35, p=45, k=42,
        temperature=24.0, humidity=58.0, rainfall=40.0,
        image_path=None,       # set to a real soil photo path to test the CNN/fallback path
        lang="en",
        output_path="outputs/soil_report_demo.pdf",
    )

    print("Soil Health Score:", result["health"]["score"], result["health"]["level"])
    print("Top crops:", result["crops"])
    print("Fertilizer suggestions:", result["fertilizer"])
    print("Alerts:", result["alerts"])
    print("\nPDF report written to outputs/soil_report_demo.pdf")
