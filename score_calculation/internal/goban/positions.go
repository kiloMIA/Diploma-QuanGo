package goban

import "github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"

func isValidPosition(pos models.Position, board models.Board) bool {
	return pos.X >= 0 && pos.X < len(board) && pos.Y >= 0 && pos.Y < len(board[0])
}

func isValidAndEmpty(board models.Board, x, y int) bool {
	return x >= 0 && x < len(board) && y >= 0 && y < len(board) && board[x][y] == "0"
}

// isEmptyBetween checks if the position between two points is empty and thus a valid connection spot
func isEmptyBetween(pos1, pos2 models.Position, board models.Board) bool {
	// Calculate mid-point between two positions (if directly adjacent, this check is trivially true for full connections)
	midX := (pos1.X + pos2.X) / 2
	midY := (pos1.Y + pos2.Y) / 2
	return board[midX][midY] == "0"
}

// Additional utility function to get all surrounding positions including diagonals
func getSurroundingPositions(pos models.Position) []models.Position {
	return []models.Position{
		{X: pos.X - 1, Y: pos.Y}, {X: pos.X + 1, Y: pos.Y},
		{X: pos.X, Y: pos.Y - 1}, {X: pos.X, Y: pos.Y + 1},
		{X: pos.X - 1, Y: pos.Y - 1}, {X: pos.X - 1, Y: pos.Y + 1},
		{X: pos.X + 1, Y: pos.Y - 1}, {X: pos.X + 1, Y: pos.Y + 1},
	}
}

func getCardinalPositions(pos models.Position) []models.Position {
	return []models.Position{
		{X: pos.X - 1, Y: pos.Y}, {X: pos.X + 1, Y: pos.Y},
		{X: pos.X, Y: pos.Y - 1}, {X: pos.X, Y: pos.Y + 1},
	}
}
