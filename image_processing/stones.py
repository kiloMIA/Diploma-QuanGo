import cv2
import numpy as np 
from scipy import ndimage
from filters import apply_watershed

def find_stones(board):
    img = board.copy()
    shifted = cv2.pyrMeanShiftFiltering(img, 21, 51)
    cv2.imshow("sifted", shifted)
    cv2.waitKey(0)
    gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)

    blackStoneThresh, black_bin = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    whiteStoneThresh, white_bin = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    apply_watershed(blackStoneThresh, black_bin, img)
    apply_watershed(whiteStoneThresh, white_bin, img)
