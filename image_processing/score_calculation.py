import numpy as np

class Territory:
    def __init__(self):
        self.num_black_territory = 0
        self.num_white_territory = 0
        self.num_black_stones = 0
        self.num_white_stones = 0
        self.num_dame = 0
        self.dame_points = []

    def add_point(self, point, status):
        if status == 'B':
            self.num_black_stones += 1
        elif status == 'W':
            self.num_white_stones += 1
        elif status == 'territory_b':
            self.num_black_territory += 1
        elif status == 'territory_w':
            self.num_white_territory += 1
        elif status == 'dame':
            self.num_dame += 1
            self.dame_points.append(point)

class GameResult:
    def __init__(self, b_score, w_score, komi):
        self.b_score = b_score
        self.w_score = w_score
        self.komi = komi

    @property
    def winner(self):
        if self.b_score > self.w_score + self.komi:
            return 'Black wins'
        else:
            return 'White wins'

    def __str__(self):
        if self.b_score > self.w_score + self.komi:
            return f'Black+{self.b_score - (self.w_score + self.komi):.1f}'
        else:
            return f'White+{(self.w_score + self.komi) - self.b_score:.1f}'

def flood_fill(board, x, y, visited, color=None):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    stack = [(x, y)]
    territory = []
    border_colors = set()

    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))
        if board[cx][cy] == '0':
            territory.append((cx, cy))
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < len(board) and 0 <= ny < len(board[0]):
                    if board[nx][ny] == '0':
                        stack.append((nx, ny))
                    else:
                        border_colors.add(board[nx][ny])
        else:
            border_colors.add(board[cx][cy])

    return territory, border_colors

def evaluate_territory(board):
    visited = set()
    territory = Territory()

    for x in range(len(board)):
        for y in range(len(board[0])):
            if (x, y) not in visited and board[x][y] == '0':
                group, borders = flood_fill(board, x, y, visited)
                if len(borders) == 1:
                    fill_with = 'territory_b' if 'B' in borders else 'territory_w'
                else:
                    fill_with = 'dame'
                for pos in group:
                    territory.add_point(pos, fill_with)
            else:
                territory.add_point((x, y), board[x][y])

    return territory

def compute_game_result(board, komi):
    territory = evaluate_territory(board)
    b_score = territory.num_black_territory + territory.num_black_stones
    w_score = territory.num_white_territory + territory.num_white_stones + komi
    return GameResult(b_score, w_score, komi)

