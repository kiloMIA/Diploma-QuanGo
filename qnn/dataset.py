import os
import torch
from PIL import Image
from torch.utils.data import Dataset


class GoBoardDataset(Dataset):
    def __init__(self, root, transforms=None):
        self.root = root
        self.transforms = transforms
        self.image_extensions = [".png", ".jpg", ".jpeg", ".JPEG"]
        self.data = self._load_data()

    def _load_data(self):
        data = []
        for folder in sorted(os.listdir(self.root)):
            folder_path = os.path.join(self.root, folder)
            if os.path.isdir(folder_path):
                for file in sorted(os.listdir(folder_path)):
                    if any(file.endswith(ext) for ext in self.image_extensions):
                        img_path = os.path.join(folder_path, file)
                        ann_path = os.path.join(
                            folder_path, file.rsplit(".", 1)[0] + ".txt"
                        )
                        if os.path.exists(ann_path):
                            data.append((img_path, ann_path))
        return data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_path, ann_path = self.data[idx]

        img = Image.open(img_path).convert("RGB")
        boxes = []
        labels = []

        with open(ann_path) as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                tokens = line.split()
                for j, token in enumerate(tokens):
                    if token == "B" or token == "W":
                        x_min = j * 32
                        y_min = i * 32
                        x_max = (j + 1) * 32
                        y_max = (i + 1) * 32
                        boxes.append([x_min, y_min, x_max, y_max])
                        labels.append(1 if token == "B" else 2)

        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        labels = torch.as_tensor(labels, dtype=torch.int64)

        if len(boxes) == 0:
            return None

        target = {"boxes": boxes, "labels": labels}

        if self.transforms is not None:
            img = self.transforms(img)

        return img, target


def collate_fn(batch):
    batch = list(filter(lambda x: x is not None, batch))
    return tuple(zip(*batch))
