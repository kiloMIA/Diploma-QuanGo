package goban

import "github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"

func identifyDamePoints(influence [19][19]int) []models.Position {
	var damePoints []models.Position
	for y := 0; y < 19; y++ {
		for x := 0; x < 19; x++ {
			if influence[y][x] == 0 {
				damePoints = append(damePoints, models.Position{X: x, Y: y})
			}
		}
	}
	return damePoints
}

func fillDamePoints(board *models.Board, damePoints []models.Position, color string) {
	for _, point := range damePoints {
		original := (*board)[point.Y][point.X]
		if original == "0" {
			(*board)[point.Y][point.X] = color
		}
	}
}
