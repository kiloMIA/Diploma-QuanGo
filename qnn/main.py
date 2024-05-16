import torch
from torch.utils.data import DataLoader, random_split
from torchvision.transforms import ToTensor
import time
import os
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

from goban_model import create_model
from dataset import GoBoardDataset, collate_fn


def train(train_dataloader, model, optimizer, device, accumulation_steps):
    model.train()
    running_loss = 0
    iteration_losses = []
    progress_bar = tqdm(train_dataloader, desc='Training', leave=True)
    optimizer.zero_grad()
    for i, data in enumerate(progress_bar):
        if not data:
            continue
        images, targets = data[0], data[1]
        images = list(image.to(device) for image in images)
        targets = [{k: v.to(device) for k, v in t.items()} for t in targets]
        loss_dict = model(images, targets)
        loss = sum(loss for loss in loss_dict.values())
        loss = loss / accumulation_steps  
        running_loss += loss.item()
        iteration_losses.append(loss.item())
        loss.backward()
        if (i + 1) % accumulation_steps == 0:  
            optimizer.step()
            optimizer.zero_grad()
        progress_bar.set_postfix({"loss": loss.item(), "left": len(train_dataloader) - (i + 1)})
    train_loss = running_loss / len(train_dataloader.dataset)
    return train_loss, iteration_losses


def val(val_dataloader, model, device):
    model.eval()
    running_loss = 0
    iteration_losses = []
    progress_bar = tqdm(val_dataloader, desc='Validation', leave=True)
    with torch.no_grad():
        for i, data in enumerate(progress_bar):
            if not data:  
                continue
            images, targets = data[0], data[1]
            images = list(image.to(device) for image in images)
            targets = [{k: v.to(device) for k, v in t.items()} for t in targets]
            outputs = model(images)
            detected_boxes = sum(len(output['boxes']) for output in outputs)
            true_boxes = sum(len(target['boxes']) for target in targets)
            accuracy = detected_boxes / true_boxes if true_boxes > 0 else 0
            iteration_losses.append(accuracy)
            progress_bar.set_postfix({"accuracy": accuracy, "left": len(val_dataloader) - (i + 1)})
    val_loss = sum(iteration_losses) / len(val_dataloader)
    return val_loss, iteration_losses


def plot_losses(train_losses, val_losses):
    epochs = range(1, len(train_losses) + 1)
    plt.figure(figsize=(10, 5))
    plt.plot(epochs, train_losses, "b", label="Training loss")
    plt.plot(epochs, val_losses, "r", label="Validation accuracy")
    plt.title("Training and validation loss/accuracy")
    plt.xlabel("Epochs")
    plt.ylabel("Loss/Accuracy")
    plt.legend()
    plt.show()


def main():
    dataset = GoBoardDataset("archive/dataset", transforms=ToTensor())

    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = random_split(dataset, [train_size, test_size])

    train_dataloader = DataLoader(
        train_dataset, batch_size=2, shuffle=True, collate_fn=collate_fn
    )
    test_dataloader = DataLoader(
        test_dataset, batch_size=2, shuffle=False, collate_fn=collate_fn
    )

    num_classes = 3
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model = create_model(num_classes, weights='DEFAULT').to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4, weight_decay=0.0005)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)

    num_epochs = 10
    accumulation_steps = 5
    train_losses = []
    val_losses = []
    iteration_log = []

    for epoch in range(num_epochs):
        start = time.time()
        train_loss, train_iteration_losses = train(train_dataloader, model, optimizer, device, accumulation_steps)
        val_loss, val_iteration_losses = val(test_dataloader, model, device)
        scheduler.step()
        print(f"Epoch #{epoch} train_loss: {train_loss}, val_loss: {val_loss}")
        end = time.time()
        print(f"Time spent {round((end - start) / 60, 1)} minutes on epoch {epoch}")
        train_losses.append(train_loss)
        val_losses.append(val_loss)

        iteration_log.append({
            "epoch": epoch,
            "train_iteration_losses": train_iteration_losses,
            "val_iteration_losses": val_iteration_losses
        })

    torch.save(model.state_dict(), "go_stone_detector.pth")

    losses_df = pd.DataFrame(
        {
            "Epoch": range(1, num_epochs + 1),
            "Train Loss": train_losses,
            "Val Loss": val_losses,
        }
    )
    losses_df.to_csv("training_losses.csv", index=False)

    iteration_df = pd.DataFrame(iteration_log)
    iteration_df.to_csv("iteration_losses.csv", index=False)

    plot_losses(train_losses, val_losses)


if __name__ == "__main__":
    main()

