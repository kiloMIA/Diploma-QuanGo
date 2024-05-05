package goban

import (
	"github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"
)

// CheckForSnapBack simulates a capture and checks for a snap-back opportunity.
func CheckForSnapBack(pos models.Position, board models.Board, currentColor string) bool {
	opponentColor := "W"
	if currentColor == "W" {
		opponentColor = "B"
	}

	originalStone := board[pos.Y][pos.X]
	board[pos.Y][pos.X] = "0" // Simulate capture

	if IsStoneInAtari(pos, board, currentColor) {
		board[pos.Y][pos.X] = opponentColor // Opponent plays here
		if IsStoneInAtari(pos, board, opponentColor) {
			board[pos.Y][pos.X] = originalStone // Restore stone
			return true
		}
	}

	board[pos.Y][pos.X] = originalStone // Restore stone
	return false
}

// CheckForSeki determines if two or more groups are in a mutual life situation (seki).
func CheckForSeki(groups [][]models.String, board models.Board) bool {
	for _, group := range groups {
		sharedLiberties := make(map[models.Position]int)
		for _, str := range group {
			liberties := GetLiberties(str, board)
			for pos := range liberties {
				sharedLiberties[pos]++
			}
		}

		for _, count := range sharedLiberties {
			if count == len(group) && CanGroupsCaptureEachOther(group, board) {
				return true
			}
		}
	}
	return false
}

// Helper function to determine if groups can safely capture each other without self-atari.
func CanGroupsCaptureEachOther(groups []models.String, board models.Board) bool {
	for _, str := range groups {
		if IsStoneInAtari(models.Position{X: str.Positions[0].X, Y: str.Positions[0].Y}, board, str.Color) {
			return false
		}
	}
	return true
}

// GetLiberties returns the set of liberties for a given string.
func GetLiberties(str models.String, board models.Board) map[models.Position]bool {
	liberties := make(map[models.Position]bool)
	for _, pos := range str.Positions {
		for _, adjPos := range getCardinalPositions(pos) {
			if isValidAndEmpty(board, adjPos.X, adjPos.Y) {
				liberties[adjPos] = true
			}
		}
	}
	return liberties
}

func IsStoneInAtari(pos models.Position, board models.Board, color string) bool {
	liberties := 0
	directions := getCardinalPositions(pos)
	for _, d := range directions {
		if isValidAndEmpty(board, d.X, d.Y) {
			liberties++
		}
	}
	return liberties == 1
}
