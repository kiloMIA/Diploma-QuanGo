import os
import torch
from torch.utils.data import Dataset
from PIL import Image

class GoBoardDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.image_files = []
        self.annotation_files = []
        
        for subdir, _, files in os.walk(root_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    self.image_files.append(os.path.join(subdir, file))
                    annotation_file = os.path.splitext(file)[0] + '.txt'
                    self.annotation_files.append(os.path.join(subdir, annotation_file))

        print(f"Found {len(self.image_files)} image files in {root_dir}")

    def __len__(self):
        return len(self.image_files)
    
    def __getitem__(self, idx):
        img_path = self.image_files[idx]
        image = Image.open(img_path).convert('RGB')
        
        annotation_path = self.annotation_files[idx]
        
        if not os.path.exists(annotation_path):
            raise FileNotFoundError(f"No such file or directory: '{annotation_path}'")
        
        with open(annotation_path, 'r') as file:
            annotation = file.read()
        
        annotation = annotation.replace('\n', ' ').split()
        annotation = [1 if x == 'B' else 2 if x == 'W' else 0 for x in annotation]
        annotation = torch.tensor(annotation).view(19, 19)
        
        if self.transform:
            image = self.transform(image)
        
        return image, annotation
