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
                        ann_path = os.path.join(folder_path, file.rsplit(".", 1)[0] + ".txt")
                        if os.path.exists(ann_path):
                            data.append((img_path, ann_path))
        return data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_path, ann_path = self.data[idx]

        img = Image.open(img_path).convert("RGB")
        annotation = []

        with open(ann_path) as f:
            lines = f.readlines()
            for line in lines:
                tokens = line.split()
                annotation.extend(tokens)

        annotation = torch.as_tensor([1 if x == 'B' else 2 if x == 'W' else 0 for x in annotation], dtype=torch.long).reshape(19, 19)

        if self.transforms is not None:
            img = self.transforms(img)

        return img, annotation

