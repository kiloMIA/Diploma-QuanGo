import torch
import torch.nn as nn
import torch.nn.functional as F

class StoneClassifierCNN(nn.Module):
    def __init__(self):
        super(StoneClassifierCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(128*32*32, 512)
        self.fc2 = nn.Linear(512, 19*19*3)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2)
        x = F.relu(self.conv3(x))
        x = F.max_pool2d(x, 2)
        x = x.view(-1, 128*32*32)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        x = x.view(-1, 3, 19, 19)
        return x

def evaluate(model, val_loader, criterion):
    model.eval()
    val_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for images, annotations in val_loader:
            outputs = model(images)
            loss = criterion(outputs, annotations)
            val_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += annotations.nelement()
            correct += (predicted == annotations).sum().item()
    accuracy = 100 * correct / total
    return val_loss / len(val_loader), accuracy
