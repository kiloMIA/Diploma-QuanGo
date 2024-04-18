import cv2
import numpy as np 
from filters import apply_watershed
from utils import auto_canny

def find_stones(board):
    img = board.copy()
    black_stones = img.copy()
    white_stones = img.copy()
    shifted = cv2.pyrMeanShiftFiltering(img, 21, 51)
    gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)

    blackStoneThresh, black_bin = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    whiteStoneThresh, white_bin = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    black_stones = apply_watershed(blackStoneThresh, black_bin, black_stones)
    white_stones = apply_watershed(whiteStoneThresh, white_bin, white_stones)
    black_centroids = find_centroids(black_stones, 'B')
    white_centroids = find_centroids(white_stones, 'W')
    image_dim = board.shape

    black_board = map_to_grid(black_centroids, image_dim, 'B')
    white_board = map_to_grid(white_centroids, image_dim, 'W')
    
    combined_board = np.where(black_board == 'B', 'B', white_board)
    combined_board = np.where(white_board == 'W', 'W', combined_board)

    print("Combined Board Representation:")
    for row in combined_board:
        print(" ".join(row))

def find_centroids(img, stone_color):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if stone_color == 'B':
        ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    else:  
        ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    centroids = []

    for contour in contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centroids.append((cx, cy))
    
    return centroids

def map_to_grid(centroids, image_dim, stone_color):
    board = np.full((19, 19), '0') 
    grid_spacing_x = image_dim[1] / 19
    grid_spacing_y = image_dim[0] / 19

    for x, y in centroids:
        grid_x = int(x / grid_spacing_x)
        grid_y = int(y / grid_spacing_y)
        grid_x = min(max(grid_x, 0), 18)
        grid_y = min(max(grid_y, 0), 18)
        board[grid_y, grid_x] = stone_color 

    return board
