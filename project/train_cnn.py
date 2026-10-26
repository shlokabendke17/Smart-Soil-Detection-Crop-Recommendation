"""
train_cnn.py
Generates a synthetic soil image dataset (if it doesn't already exist in data/soil_images)
and trains the PyTorch CNN model to detect soil types.
Saves model weights to models/soil_cnn.pth.
"""

import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from PIL import Image, ImageFilter
import numpy as np

# Ensure project root is importable
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from models.cnn_soil_classifier import SoilCNN, SOIL_CLASSES, WEIGHTS_PATH, TRAIN_DIR, IMG_SIZE

# Color profiles for generating synthetic training images if needed
SOIL_COLORS = {
    "Sandy": (194, 178, 128),
    "Clay":  (150, 130, 110),
    "Loamy": (110, 80, 55),
    "Black": (45, 42, 40),
    "Red":   (150, 70, 45)
}

def generate_synthetic_dataset(num_images_per_class=30):
    """Generates synthetic soil images using fast vectorized numpy operations."""
    print("Generating synthetic soil images dataset for training...")
    os.makedirs(TRAIN_DIR, exist_ok=True)
    
    for category, base_color in SOIL_COLORS.items():
        cat_dir = os.path.join(TRAIN_DIR, category)
        os.makedirs(cat_dir, exist_ok=True)
        
        # Check if already populated
        existing = len([f for f in os.listdir(cat_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        if existing >= num_images_per_class:
            print(f"  Category '{category}' already has {existing} images. Skipping generation.")
            continue
            
        print(f"  Generating {num_images_per_class} images for category: {category}...")
        for i in range(num_images_per_class):
            # Create a base color array with minor randomized variation
            color_var = np.array([
                max(0, min(255, c + np.random.randint(-15, 16)))
                for c in base_color
            ], dtype=np.int16)
            
            # Create a 3D numpy array representing the image
            arr = np.zeros((IMG_SIZE[1], IMG_SIZE[0], 3), dtype=np.int16)
            arr += color_var
            
            # Generate procedural noise using vectorized numpy functions (extremely fast)
            noise = np.random.randint(-12, 13, size=arr.shape)
            arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
            
            # Convert back to PIL Image
            img = Image.fromarray(arr)
            
            # Apply slight blur to blend texture
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            img_path = os.path.join(cat_dir, f"synth_{i:03d}.jpg")
            img.save(img_path)
    print("Dataset generation complete!")

def train_model(epochs=5, batch_size=16, lr=0.001):
    # Make sure we have training data
    generate_synthetic_dataset()
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nTraining on device: {device}")
    
    # Dataset transforms & loaders
    transform = transforms.Compose([
        transforms.Resize(IMG_SIZE),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    
    dataset = datasets.ImageFolder(TRAIN_DIR, transform=transform)
    
    # Ensure mapping classes correctly to our SOIL_CLASSES ordering
    print("Dataset class-to-idx mapping:", dataset.class_to_idx)
    
    # Validation split
    train_size = int(0.85 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    model = SoilCNN(num_classes=len(SOIL_CLASSES)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    best_acc = 0.0
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
        epoch_loss = running_loss / len(train_dataset)
        epoch_acc = correct / total * 100
        
        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
                
        val_acc = val_correct / val_total * 100 if val_total > 0 else 100.0
        print(f"Epoch [{epoch+1}/{epochs}] - Loss: {epoch_loss:.4f} | Train Acc: {epoch_acc:.1f}% | Val Acc: {val_acc:.1f}%")
        
        # Save model
        if val_acc >= best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), WEIGHTS_PATH)
            
    print(f"\nTraining completed! Model saved to: {WEIGHTS_PATH} (Best Val Acc: {best_acc:.1f}%)")

if __name__ == "__main__":
    train_model(epochs=5)
