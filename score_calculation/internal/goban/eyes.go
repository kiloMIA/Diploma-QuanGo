package goban

import "github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"

func IdentifyEyesAndEyelikes(str models.String, board models.Board) (int, int, int) {
	actualEyes, specialEyes, eyelikes := 0, 0, 0

	checkedPositions := make(map[models.Position]bool)

	for _, pos := range str.Positions {
		// Check all surrounding positions to identify potential eyes
		surroundingPositions := getSurroundingPositions(pos)
		for _, eyePos := range surroundingPositions {
			// Ensure each position is only checked once
			if _, checked := checkedPositions[eyePos]; !checked && isValidPosition(eyePos, board) {
				checkedPositions[eyePos] = true
				if board[eyePos.X][eyePos.Y] == "0" { // Check only empty positions
					if isActualEye(eyePos, str, board) {
						actualEyes++
					} else if isSpecialEye(eyePos, str, board) {
						specialEyes++
					} else if isEyelike(eyePos, str, board) {
						eyelikes++
					}
				}
			}
		}
	}

	return actualEyes, specialEyes, eyelikes
}

func isActualEye(pos models.Position, str models.String, board models.Board) bool {
	surrounding := getCardinalPositions(pos)
	for _, adjPos := range surrounding {
		if !isValidPosition(adjPos, board) || board[adjPos.X][adjPos.Y] != str.Color {
			return false
		}
	}
	return true
}

func isSpecialEye(pos models.Position, str models.String, board models.Board) bool {
	surrounding := getSurroundingPositions(pos)
	friendlyCount, emptyCount := 0, 0
	for _, adjPos := range surrounding {
		if isValidPosition(adjPos, board) {
			if board[adjPos.X][adjPos.Y] == str.Color {
				friendlyCount++
			} else if board[adjPos.X][adjPos.Y] == "0" {
				emptyCount++
			}
		}
	}
	// At least 6 friendly and up to 2 empty (including corners)
	return friendlyCount >= 6 && emptyCount <= 2
}

func isEyelike(pos models.Position, str models.String, board models.Board) bool {
	surrounding := getSurroundingPositions(pos)
	friendlyCount, emptyCount := 0, 0
	for _, adjPos := range surrounding {
		if isValidPosition(adjPos, board) {
			if board[adjPos.X][adjPos.Y] == str.Color {
				friendlyCount++
			} else if board[adjPos.X][adjPos.Y] == "0" {
				emptyCount++
			}
		}
	}
	// At least 5 friendly and the remaining spots empty
	return friendlyCount >= 5 && (len(surrounding)-friendlyCount) == emptyCount
}
