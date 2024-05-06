import os
import yaml
import tqdm
from PIL import Image 
import os
import matplotlib.pyplot as plt

def read_annotation(path):
    with open(path) as func:
        annotation = func.read()
    return annotation

def load_board_info(path):
    with open(path) as func:
        board_annotation = yaml.load(func, Loader=yaml.FullLoader)
    return board_annotation

def get_dataset(path):
    dataset = []
    for dirname, _, filenames in tqdm.tqdm(os.walk(path)):
        for filename in filenames:
            if filename.endswith('.jpg') or filename.endswith('.JPG') or filename.endswith('.png'):
                row = {}
                image = Image.open(os.path.join(dirname, filename))
                row['image'] = image
                row['path'] = os.path.join(dirname, filename)

                if os.path.exists(os.path.join(dirname, filename[:-4] + '.txt')):
                    row['annotation'] = read_annotation(os.path.join(dirname, filename[:-4] + '.txt'))
                    
                if os.path.exists(os.path.join(dirname, filename[:-4] + '.TXT')):
                    row['annotation'] = read_annotation(os.path.join(dirname, filename[:-4] + '.TXT'))
                    
                if os.path.exists(os.path.join(dirname, 'board_extractor_state.yml')):
                    row['pts_clicks'] = load_board_info(os.path.join(dirname, 'board_extractor_state.yml'))['pts_clicks']
                    
                dataset.append(row)
    return dataset