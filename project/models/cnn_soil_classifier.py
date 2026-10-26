"""
cnn_soil_classifier.py
CNN-based soil image classifier, built with PyTorch to the requested architecture:

    Input (224x224x3)
      -> Conv2D(32) + ReLU -> MaxPooling
      -> Conv2D(64) + ReLU -> MaxPooling
      -> Conv2D(128) + ReLU -> MaxPooling
      -> Flatten -> Dense(128) -> Dropout -> Dense(num_classes)

Returns soil type, confidence score, RGB distribution, and agronomic profile traits.
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from .fallback_image_classifier import SOIL_PROFILES, classify_by_color

SOIL_CLASSES = ["Sandy", "Clay", "Loamy", "Black", "Red"]
IMG_SIZE = (224, 224)

HERE = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_PATH = os.path.join(HERE, "soil_cnn.pth")


# ── PyTorch CNN Architecture ──────────────────────────────────────────────────
class SoilCNN(nn.Module):
    def __init__(self, num_classes: int = len(SOIL_CLASSES)):
        super(SoilCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(128 * 28 * 28, 128)
        self.dropout = nn.Dropout(0.4)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 128 * 28 * 28)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


def predict(image_path: str) -> dict:
    """Returns {'soil_type': str, 'confidence': float, 'method': str, 'profile': dict}."""
    if os.path.exists(WEIGHTS_PATH):
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = SoilCNN()
            model.load_state_dict(torch.load(WEIGHTS_PATH, map_location=device))
            model.to(device)
            model.eval()

            preprocess = transforms.Compose([
                transforms.Resize(IMG_SIZE),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
            ])

            img = Image.open(image_path).convert("RGB")
            tensor = preprocess(img).unsqueeze(0).to(device)

            with torch.no_grad():
                outputs = model(tensor)
                probs = F.softmax(outputs, dim=1)[0]
                idx = torch.argmax(probs).item()
                confidence = probs[idx].item() * 100

            predicted_type = SOIL_CLASSES[idx]
            profile = SOIL_PROFILES.get(predicted_type, {})

            # Also compute avg RGB
            resized = img.resize((32, 32))
            pix = list(resized.getdata())
            r = round(sum(p[0] for p in pix) / len(pix), 1)
            g = round(sum(p[1] for p in pix) / len(pix), 1)
            b = round(sum(p[2] for p in pix) / len(pix), 1)

            return {
                "soil_type": predicted_type,
                "confidence": round(float(confidence), 1),
                "method": "CNN (PyTorch Deep Learning)",
                "rgb": {"r": r, "g": g, "b": b},
                "profile": profile
            }
        except Exception as e:
            print(f"Error executing PyTorch model: {e}. Falling back to color-heuristic.")

    return classify_by_color(image_path)
