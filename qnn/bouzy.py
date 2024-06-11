import numpy as np

board_size = 19


def initialize_influence(board):
    influence = np.zeros((board_size, board_size), dtype=int)
    for y in range(board_size):
        for x in range(board_size):
            if board[y, x] == "B":
                influence[y, x] = 64  # Positive high value for black
            elif board[y, x] == "W":
                influence[y, x] = -64  # Negative high value for white
    return influence


def spread_influence(x, y, board, influence, value):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for d in directions:
        nx, ny = x + d[0], y + d[1]
        if 0 <= nx < board_size and 0 <= ny < board_size:
            if board[ny, nx] == "." or influence[ny, nx] * value >= 0:
                influence[ny, nx] += value // 64


def dilation(board, influence, steps):
    for _ in range(steps):
        temp_influence = influence.copy()
        for y in range(board_size):
            for x in range(board_size):
                spread_influence(x, y, board, temp_influence, influence[y, x])
        influence[:] = temp_influence


def check_influence_removal(x, y, influence, value):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    count_opposite, count_same = 0, 0

    for d in directions:
        nx, ny = x + d[0], y + d[1]
        if 0 <= nx < board_size and 0 <= ny < board_size:
            neighbor_value = influence[ny, nx]
            if neighbor_value * value < 0:
                count_opposite += 1
            elif neighbor_value * value > 0:
                count_same += 1

    if count_opposite > count_same:
        influence[y, x] = 0


def erosion(influence, steps):
    for _ in range(steps):
        temp_influence = influence.copy()
        for y in range(board_size):
            for x in range(board_size):
                if temp_influence[y, x] != 0:
                    check_influence_removal(x, y, temp_influence, temp_influence[y, x])
        influence[:] = temp_influence
