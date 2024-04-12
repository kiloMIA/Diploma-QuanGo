import cv2
import definitions
from board import find_board
from stones import find_stones

def main():
    image = cv2.imread("image/MLC_1137.JPG")
    board = find_board(image)
    stones = find_stones(board)


if __name__ == "__main__":
    main()
