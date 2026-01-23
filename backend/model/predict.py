import os
import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add project root to path for config import
import sys
sys.path.insert(0, PROJECT_ROOT)
from config import LABELS, IMG_SIZE

# Model path
MODEL_PATH = os.path.join(PROJECT_ROOT, "model", "arthritis_severity_model.pth")
model = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Image transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def load_model():
    global model
    if model is None:
        if os.path.exists(MODEL_PATH):
            # Build model architecture
            model = models.resnet50(weights=None)
            num_features = model.fc.in_features
            model.fc = nn.Sequential(
                nn.Linear(num_features, 256),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(256, 5)
            )
            
            # Load saved weights
            checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
            model.load_state_dict(checkpoint['model_state_dict'])
            model = model.to(device)
            model.eval()
            print(f"Model loaded from: {MODEL_PATH}")
            print(f"Model validation accuracy: {checkpoint['val_acc']:.2f}%")
        else:
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Please run train_model.py first to train the model."
            )
    return model

def predict_severity(path):
    """Predict osteoarthritis severity from an X-ray image."""
    m = load_model()
    
    # Load and preprocess image
    img = Image.open(path).convert('RGB')
    img_tensor = transform(img).unsqueeze(0).to(device)
    
    # Predict
    with torch.no_grad():
        outputs = m(img_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted = probabilities.max(1)
    
    class_idx = predicted.item()
    confidence_score = confidence.item()
    
    return LABELS[class_idx], confidence_score

if __name__ == "__main__":
    # Test prediction
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        severity, confidence = predict_severity(image_path)
        print(f"Severity: {severity}")
        print(f"Confidence: {confidence:.2%}")
    else:
        print("Usage: python predict.py <image_path>")
