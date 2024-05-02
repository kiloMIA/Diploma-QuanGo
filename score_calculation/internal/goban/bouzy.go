package goban

import (
	"github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"
)

const boardSize = 19

func Dilation(board [boardSize][boardSize]string, steps int) [boardSize][boardSize]int {
	influence := [boardSize][boardSize]int{}

	for step := 0; step < steps; step++ {
		tempInfluence := influence
		for y := 0; y < boardSize; y++ {
			for x := 0; x < boardSize; x++ {
				if board[y][x] != "0" {
					spreadInfluence(x, y, board, &tempInfluence, board[y][x])
				}
			}
		}
		influence = tempInfluence
	}

	return influence
}

func Erosion(influence *[boardSize][boardSize]int, steps int) {
	for step := 0; step < steps; step++ {
		tempInfluence := *influence
		for y := 0; y < boardSize; y++ {
			for x := 0; x < boardSize; x++ {
				if tempInfluence[y][x] != 0 {
					checkInfluenceRemoval(x, y, &tempInfluence)
				}
			}
		}
		*influence = tempInfluence
	}
}

func spreadInfluence(x, y int, board [boardSize][boardSize]string, influence *[boardSize][boardSize]int, color string) {
	directions := []models.Position{
		{X: 1, Y: 0}, {X: -1, Y: 0}, {X: 0, Y: 1}, {X: 0, Y: -1},
	}

	for _, d := range directions {
		nx, ny := x+d.X, y+d.Y
		if nx >= 0 && nx < boardSize && ny >= 0 && ny < boardSize && board[ny][nx] == "0" {
			if color == "B" {
				(*influence)[ny][nx] += 1
			} else if color == "W" {
				(*influence)[ny][nx] -= 1
			}
		}
	}
}

func checkInfluenceRemoval(x, y int, influence *[boardSize][boardSize]int) {
	currentValue := (*influence)[y][x]
	shouldRemove := true

	directions := []models.Position{
		{X: 1, Y: 0}, {X: -1, Y: 0}, {X: 0, Y: 1}, {X: 0, Y: -1},
	}

	for _, d := range directions {
		nx, ny := x+d.X, y+d.Y
		if nx >= 0 && nx < boardSize && ny >= 0 && ny < boardSize {
			if (*influence)[ny][nx]*currentValue > 0 { // Same sign influence
				shouldRemove = false
				break
			}
		}
	}

	if shouldRemove {
		(*influence)[y][x] = 0
	}
}
