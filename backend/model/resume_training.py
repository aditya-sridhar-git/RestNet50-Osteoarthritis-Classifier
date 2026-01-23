"""
Resume training from a saved checkpoint.
Usage: python model/resume_training.py [--epochs N]
"""
import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

# Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(PROJECT_ROOT, "model", "arthritis_severity_model.pth")

# Data directories
train_dir = os.path.join(PROJECT_ROOT, "data", "sample_xrays", "train")
test_dir = os.path.join(PROJECT_ROOT, "data", "sample_xrays", "test")

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Data transforms
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load datasets
train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
test_dataset = datasets.ImageFolder(test_dir, transform=test_transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=0)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=0)

print(f"Training samples: {len(train_dataset)}, Test samples: {len(test_dataset)}")

def build_model():
    """Build model architecture."""
    model = models.resnet50(weights=None)
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_features, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, 5)
    )
    return model

def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    for batch_idx, (inputs, labels) in enumerate(loader):
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        if (batch_idx + 1) % 20 == 0:
            print(f"  Batch {batch_idx + 1}/{len(loader)}, Loss: {loss.item():.4f}")
    return running_loss / len(loader), 100. * correct / total

def validate(model, loader, criterion, device):
    model.eval()
    running_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
    return running_loss / len(loader), 100. * correct / total

def main():
    parser = argparse.ArgumentParser(description="Resume training from checkpoint")
    parser.add_argument("--epochs", type=int, default=5, help="Additional epochs to train")
    args = parser.parse_args()

    # Check if checkpoint exists
    if not os.path.exists(MODEL_PATH):
        print(f"No checkpoint found at {MODEL_PATH}")
        print("Please run train_model.py first or ensure the checkpoint file exists.")
        return

    # Load checkpoint
    print(f"\nLoading checkpoint from: {MODEL_PATH}")
    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
    
    start_epoch = checkpoint.get('epoch', 0) + 1
    best_acc = checkpoint.get('val_acc', 0)
    
    print(f"Resuming from epoch {start_epoch} with best accuracy: {best_acc:.2f}%")

    # Build and load model
    model = build_model()
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)

    # Setup optimizer and load state
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.fc.parameters(), lr=0.001)
    if 'optimizer_state_dict' in checkpoint:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    # Training loop
    print(f"\n{'='*50}")
    print(f"Resuming Training for {args.epochs} more epochs...")
    print(f"{'='*50}\n")

    for epoch in range(args.epochs):
        current_epoch = start_epoch + epoch
        print(f"Epoch {current_epoch + 1}")
        print("-" * 30)
        
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate(model, test_loader, criterion, device)
        
        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Save if improved
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({
                'epoch': current_epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'class_to_idx': train_dataset.class_to_idx
            }, MODEL_PATH)
            print(f"Model saved! New best accuracy: {best_acc:.2f}%")
        print()

    print(f"{'='*50}")
    print(f"Training Complete! Best Validation Accuracy: {best_acc:.2f}%")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
