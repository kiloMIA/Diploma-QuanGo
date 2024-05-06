import matplotlib.pyplot as plt
from load_data import get_dataset

ROOT = 'pictures/dataset'

def visualize_datapoint(datapoint):
    print(datapoint['path'])
    plt.figure(figsize=(8,8))
    plt.imshow(datapoint['image'])
    plt.scatter([pt[0] for pt in datapoint['pts_clicks']], [pt[1] for pt in datapoint['pts_clicks']], c='red', s=100)
    plt.show()

    annotation = datapoint['annotation']
    print(annotation)
    
    annotation = datapoint['pts_clicks']
    print(annotation)    

data = get_dataset(ROOT)

visualize_datapoint(data[1])


