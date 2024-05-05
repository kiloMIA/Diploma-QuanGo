package goban

import (
	"github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"
)

type LibertyChangeType int

const (
	NonReducing LibertyChangeType = iota // Check for non-reducing liberty moves
	Increasing                           // Check for increasing liberty moves
)

func EvaluateLibertyValue(str models.String, board models.Board) float64 {
	totalValue := 0.0
	for _, pos := range str.Positions {
		adjacentPositions := getCardinalPositions(pos)
		for _, adjPos := range adjacentPositions {
			if isValidAndEmpty(board, adjPos.X, adjPos.Y) {
				value := 1.0 // Base value of a liberty

				if putsOpponentInAtari(adjPos, str.Color, board) {
					value *= 2.0 // Worth twice if an opponent's stone here would be in atari
				}

				// Check if placing a stone does not reduce liberties
				if canPlaceFriendlyStone(adjPos, str, board, NonReducing) {
					value *= 1.333
				}

				// Check if placing a stone increases liberties
				if canPlaceFriendlyStone(adjPos, str, board, Increasing) {
					value *= 1.5
				}

				totalValue += value
			}
		}
	}
	return totalValue
}

func putsOpponentInAtari(pos models.Position, currentColor string, board models.Board) bool {
	opponentColor := "B"
	if currentColor == "B" {
		opponentColor = "W"
	}
	// Simulate placing an opponent stone
	original := board[pos.X][pos.Y]
	board[pos.X][pos.Y] = opponentColor
	atari := countLiberties(models.String{Positions: []models.Position{pos}, Color: opponentColor}, board) == 1
	board[pos.X][pos.Y] = original // Restore original state
	return atari
}

func canPlaceFriendlyStone(pos models.Position, str models.String, board models.Board, changeType LibertyChangeType) bool {
	original := board[pos.X][pos.Y]
	originalLiberties := countLiberties(str, board) // calculate before placing the stone
	board[pos.X][pos.Y] = str.Color
	newLiberties := countLiberties(str, board)
	board[pos.X][pos.Y] = original // Restore original state

	switch changeType {
	case NonReducing:
		return newLiberties >= originalLiberties
	case Increasing:
		return newLiberties > originalLiberties
	default:
		return false
	}
}

func countLiberties(str models.String, board models.Board) int {
	liberties := make(map[models.Position]bool)
	for _, pos := range str.Positions {
		// Check all adjacent positions
		adjacentPositions := []models.Position{
			{X: pos.X - 1, Y: pos.Y}, // Up
			{X: pos.X + 1, Y: pos.Y}, // Down
			{X: pos.X, Y: pos.Y - 1}, // Left
			{X: pos.X, Y: pos.Y + 1}, // Right
		}
		for _, adjPos := range adjacentPositions {
			if isValidAndEmpty(board, adjPos.X, adjPos.Y) {
				liberties[adjPos] = true
			}
		}
	}
	return len(liberties)
}
