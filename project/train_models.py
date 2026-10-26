"""
train_models.py
Trains and saves the crop-recommendation and fertilizer ML models
from the bundled CSV datasets.

Run: python train_models.py
"""

from models import crop_model, fertilizer_model


def main():
    print("Training crop recommendation model (Crop_recommendation.csv)...")
    crop_info = crop_model.train()
    print(f"  -> test accuracy: {crop_info['test_accuracy']:.4f} "
          f"across {crop_info['n_classes']} crop classes\n")

    print("Training fertilizer cross-check model (Fertilizer_Prediction.csv)...")
    fert_info = fertilizer_model.train()
    print(f"  -> test accuracy: {fert_info['test_accuracy']:.4f}\n")

    print("Done. Models saved under models/*.joblib")


if __name__ == "__main__":
    main()
