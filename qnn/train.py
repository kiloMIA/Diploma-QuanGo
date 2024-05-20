# train.py
import os
import torch
import time
import pickle
import logging
from torch.utils.data import DataLoader
from torchvision import transforms
from torch.nn import CrossEntropyLoss
from torch.optim import Adam
from tqdm import tqdm
from goban_model import StoneClassifierCNN
from dataset import GoBoardDataset

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

def train():
    OUTPUT_PATH = "output"
    BASE_PATH = "archive/dataset"
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    PIN_MEMORY = True if DEVICE == "cuda" else False
    MEAN = [0.485, 0.456, 0.406]
    STD = [0.229, 0.224, 0.225]
    INIT_LR = 1e-4
    NUM_EPOCHS = 10
    BATCH_SIZE = 4

    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    logger.info("Loading dataset...")

    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=MEAN, std=STD),
        ]
    )

    trainDS = GoBoardDataset(root=BASE_PATH, transforms=transform)
    testDS = GoBoardDataset(root=BASE_PATH, transforms=transform)

    logger.info(f"Total training samples: {len(trainDS)}")
    logger.info(f"Total test samples: {len(testDS)}")

    trainLoader = DataLoader(
        trainDS,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=os.cpu_count(),
        pin_memory=PIN_MEMORY,
        collate_fn=collate_fn,
    )
    testLoader = DataLoader(
        testDS,
        batch_size=BATCH_SIZE,
        num_workers=os.cpu_count(),
        pin_memory=PIN_MEMORY,
        collate_fn=collate_fn,
    )

    model = StoneClassifierCNN().to(DEVICE)
    criterion = CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=INIT_LR)

    logger.info("Training the network...")
    startTime = time.time()

    for epoch in range(NUM_EPOCHS):
        model.train()
        running_loss = 0.0
        train_correct = 0

        logger.info(f"Starting epoch {epoch + 1}/{NUM_EPOCHS}")

        for images, annotations in tqdm(trainLoader):
            images = images.to(DEVICE)
            annotations = annotations.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, annotations)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            train_correct += (
                (outputs.argmax(1) == annotations).type(torch.float).sum().item()
            )

        avg_train_loss = running_loss / len(trainLoader)
        train_accuracy = train_correct / (len(trainDS) * 19 * 19)

        logger.info(
            f"Epoch {epoch + 1}/{NUM_EPOCHS} - Train Loss: {avg_train_loss:.6f}, Train Accuracy: {train_accuracy:.4f}"
        )

    endTime = time.time()
    logger.info(f"Total time taken to train the model: {endTime - startTime:.2f}s")

    logger.info("Saving object detector model...")
    torch.save(model.state_dict(), "output/detector.pth")

    logger.info("Saving label encoder...")
    with open("output/le.pickle", "wb") as f:
        f.write(pickle.dumps(None))

    logger.info("Training complete!")

def collate_fn(batch):
    batch = list(filter(lambda x: x is not None, batch))
    if len(batch) == 0:
        return None
    images, targets = zip(*batch)
    return torch.stack(images, 0), torch.stack(targets, 0)

if __name__ == "__main__":
    train()

