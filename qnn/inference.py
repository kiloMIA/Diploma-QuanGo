import os
import torch
import logging
import numpy as np
from PIL import Image
from torchvision import transforms
from goban_model import StoneClassifierCNN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def load_model(model_path, device):
    model = StoneClassifierCNN().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model

def preprocess_image(image_path, mean, std):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std)
    ])
    image = Image.open(image_path).convert("RGB")
    return transform(image).unsqueeze(0)

def decode_predictions(preds):
 
    board = preds.argmax(1).cpu().numpy().reshape(19, 19)
    
   
    char_board = np.full(board.shape, '.', dtype=str)
    
    char_board[board == 0] = '.'  
    char_board[board == 1] = 'B'  
    char_board[board == 2] = 'W'  
    
    return char_board

def load_annotations(annotation_path):
    with open(annotation_path, 'r') as file:
        lines = file.readlines()
        annotations = [line.strip().split() for line in lines]
        if len(annotations) != 19 or any(len(row) != 19 for row in annotations):
            raise ValueError("Annotation file does not have the correct dimensions (19x19).")
    return np.array(annotations)

def print_boards(predicted_board, true_board):
    print("Predicted Go Board State:")
    for row in predicted_board:
        print(" ".join(row))
    print("\nTrue Go Board State:")
    for row in true_board:
        print(" ".join(row))
    print("\n" + "="*50 + "\n")

def main():
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    MEAN = [0.485, 0.456, 0.406]
    STD = [0.229, 0.224, 0.225]
    MODEL_PATH = "output/detector.pth"

    logger.info("Loading model...")
    model = load_model(MODEL_PATH, DEVICE)

    base_folder = "archive"

    for root, _, files in os.walk(base_folder):
        for file in files:
            if file.endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(root, file)
                annotation_path = os.path.join(root, file.rsplit(".", 1)[0] + ".txt")

                if not os.path.exists(annotation_path):
                    logger.warning(f"No annotation file found for {image_path}")
                    continue

                logger.info(f"Processing image: {image_path}")

                image = preprocess_image(image_path, MEAN, STD).to(DEVICE)

                try:
                    true_board = load_annotations(annotation_path)
                except ValueError as e:
                    logger.error(f"Error loading annotation file {annotation_path}: {e}")
                    continue

                with torch.no_grad():
                    preds = model(image)

                predicted_board = decode_predictions(preds)

                print_boards(predicted_board, true_board)

if __name__ == "__main__":
    main()

