# 🌱 Smart Soil Detection & Crop Recommendation System

A hybrid system combining:
- **Machine Learning** on numeric soil parameters (pH, N, P, K) + weather → crop & fertilizer decisions
- **CNN image classification** of soil photos → *reference-only* soil-type display
- **Rule-based agronomic logic** → soil health score, nutrient advisory, risk alerts
- **AI-generated PDF report** in English / Hindi / Marathi

## 🚫 The one rule the whole design revolves around

> **The CNN's soil-type prediction is never used to recommend crops or fertilizers.**
> All agricultural decisions come exclusively from `core/advisory.py` and
> `models/crop_model.py`, which only ever see pH, N, P, K, temperature,
> humidity, and rainfall. The CNN output only reaches the PDF report, labeled
> "reference only."

You can verify this by reading `main.py`: `cnn_result` is computed but never
passed into `crop_model.recommend_top_k()` or `suggest_fertilizer()`.

## What's real vs. what's a documented fallback

| Component | Status |
|---|---|
| Crop recommendation (`models/crop_model.py`) | **Real**, trained on the supplied `Crop_recommendation.csv` (2,200 rows, 22 crops). RandomForest, ~99.5% held-out test accuracy. |
| Fertilizer cross-check (`models/fertilizer_model.py`) | **Real**, trained on the supplied `Fertilizer Prediction.csv` (99 rows, 7 fertilizer classes). ~95% held-out test accuracy. Secondary/optional — the primary fertilizer advice is rule-based (see below). |
| Fertilizer advice / soil-health score / advisory / risk alerts | **Rule-based**, transparent, agronomically-grounded thresholds — not a black box, and not dependent on external image data. |
| CNN soil-image classifier (`models/cnn_soil_classifier.py`) | **Architecture is implemented exactly as specified**, using `tf.keras` (Conv2D 32→64→128, MaxPooling, Dense 128, Dropout, Softmax). **No labeled soil-image dataset was supplied** with this project (only the two tabular CSVs), and this sandbox has no TensorFlow and no internet access to fetch one. So there are no trained weights (`soil_cnn.h5`) included. |
| CNN fallback (`models/fallback_image_classifier.py`) | Automatically used whenever `soil_cnn.h5` doesn't exist or TensorFlow isn't installed — a transparent color-heuristic (compares average RGB against reference soil colors). Every prediction is labeled `"method": "Fallback (color heuristic)"` so it's never mistaken for the real CNN. This keeps the *full pipeline* runnable end-to-end today. |
| Hindi / Marathi PDF text | Renders correctly **if** you drop a Unicode Devanagari TTF (e.g. Noto Sans Devanagari) into `report/fonts/`. Without one, reportlab's built-in fonts can't draw Devanagari glyphs, so the system **automatically and visibly falls back to English** with a note in the PDF — rather than printing broken tofu boxes. |

## To train the real CNN on your own image dataset

```
data/soil_images/
    Sandy/*.jpg
    Clay/*.jpg
    Loamy/*.jpg
    Black/*.jpg
    Red/*.jpg
```

```bash
pip install tensorflow
python -c "from models.cnn_soil_classifier import train; train(epochs=15)"
```

This saves `models/soil_cnn.h5`; `models/cnn_soil_classifier.py::predict()` will
automatically pick it up and stop using the fallback.

## Project layout

```
project/
├── data/
│   ├── Crop_recommendation.csv
│   └── Fertilizer_Prediction.csv
├── core/
│   ├── soil_health.py       # 0-100 soil health score
│   ├── advisory.py          # NPK-deficiency fertilizer advice + improvement tips
│   ├── risk_alerts.py       # rainfall/humidity/temperature warnings
│   └── i18n.py              # en/hi/mr strings
├── models/
│   ├── crop_model.py            # RandomForest, trained on Crop_recommendation.csv
│   ├── fertilizer_model.py      # RandomForest, trained on Fertilizer_Prediction.csv (secondary)
│   ├── cnn_soil_classifier.py   # tf.keras CNN (architecture + train + predict)
│   └── fallback_image_classifier.py  # color-heuristic fallback
├── report/
│   ├── pdf_report.py         # reportlab PDF builder
│   └── fonts/                # drop a Devanagari TTF here for hi/mr
├── outputs/                  # generated PDF reports land here
├── train_models.py           # trains + saves crop_model & fertilizer_model
├── main.py                   # orchestrates the full pipeline; has a CLI demo
└── requirements.txt
```

## Quick start

```bash
pip install -r requirements.txt      # tensorflow line optional
python train_models.py               # trains & saves the two RandomForest models
python main.py                       # runs the demo pipeline -> outputs/soil_report_demo.pdf
```

Programmatic use:

```python
from main import run_pipeline

result = run_pipeline(
    ph=6.3, n=35, p=45, k=42,
    temperature=24.0, humidity=58.0, rainfall=40.0,
    image_path="path/to/soil_photo.jpg",   # optional; omit to skip CNN entirely
    lang="en",                              # "en" | "hi" | "mr"
    output_path="outputs/my_report.pdf",
)
```

`result` contains the soil health score, top-3 crop recommendations,
fertilizer suggestions, advisory text, and risk alerts as plain Python
dicts/lists — useful if you want to build a UI on top instead of (or in
addition to) the PDF.
