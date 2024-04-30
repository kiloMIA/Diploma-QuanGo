import cv2
import definitions
from board import find_board
from stones import find_stones
from score_calculation import compute_game_result


def main():
    image = cv2.imread("image/nWTxyYr.jpg")
    board = find_board(image)
    stones = find_stones(board)
    game_result = compute_game_result(stones, 6.5)
    print("White Score: ", game_result.w_score)
    print("Black Score: ", game_result.b_score)


if __name__ == "__main__":
    main()
