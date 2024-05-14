import time

from torch.utils.data import DataLoader, random_split
import torchvision.transforms as transforms
import torch.nn as nn
import torch.optim as optim

from dataset import GoBoardDataset
from goban_model import StoneClassifierCNN, evaluate

def main():
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor()
    ])

    dataset = GoBoardDataset(root_dir='archive/dataset', transform=transform)
    
    print(f"Total dataset size: {len(dataset)}")
    
    if len(dataset) == 0:
        print("No images found in the dataset. Please check the dataset path and content.")
        return

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size

    if train_size == 0 or val_size == 0:
        print("Dataset too small to split. Please add more data.")
        return

    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False)
    
    model = StoneClassifierCNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    num_epochs = 10

    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        start_time = time.time()
        
        for batch_idx, (images, annotations) in enumerate(train_loader):
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, annotations)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

            if batch_idx % 10 == 0: 
                print(f"Epoch [{epoch+1}/{num_epochs}], Batch [{batch_idx+1}/{len(train_loader)}], Loss: {loss.item():.4f}")
        
        avg_loss = running_loss / len(train_loader)
        epoch_time = time.time() - start_time
        print(f"Epoch [{epoch+1}/{num_epochs}] completed in {epoch_time:.2f} seconds, Average Loss: {avg_loss:.4f}")

    val_loss, val_accuracy = evaluate(model, val_loader, criterion)
    print(f'Validation Loss: {val_loss:.4f}, Validation Accuracy: {val_accuracy:.2f}%')

if __name__ == "__main__":
    main()

