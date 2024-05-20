package rules

import (
	"github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/goban"
	"github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"
)

func CalculateScore(board models.Board, blackPrisoners, whitePrisoners int, komi float64) (float64, float64) {
	strings := make([]models.String, 0)
	visited := make([][]bool, len(board))
	for i := range visited {
		visited[i] = make([]bool, len(board[i]))
	}

	// Identify strings
	for y, row := range board {
		for x, stone := range row {
			if stone != "0" && !visited[y][x] {
				str := models.String{Color: stone}
				goban.ExploreString(x, y, board, visited, stone, &str.Positions)
				strings = append(strings, str)
			}
		}
	}

	groups := goban.GroupStrings(strings, board)
	influence := goban.InitializeInfluence(board)
	goban.Dilation(board, &influence, 8)
	goban.Erosion(&influence, 21)

	// Initialize scores
	var blackScore, whiteScore float64
	blackScore, whiteScore = float64(blackPrisoners), float64(whitePrisoners)+komi

	var aliveGroups []models.Group
	for _, group := range groups {
		totalEyes, totalLiberties, totalTerritory := 0, 0, 0
		sekiDetected := goban.CheckForSeki([]models.Group{group}, board)
		snapBackDetected := false

		for i := 0; i < len(group.Strings)-1; i++ {
			for j := i + 1; j < len(group.Strings); j++ {
				if goban.CheckForSnapBack(group.Strings[i], group.Strings[j], board) {
					snapBackDetected = true
				}
			}
		}

		for _, str := range group.Strings {
			actualEyes, _, _ := goban.IdentifyEyesAndEyelikes(str, board)
			libertyValue := goban.EvaluateLibertyValue(str, board)
			totalEyes += actualEyes
			totalLiberties += int(libertyValue)
			for _ = range str.Positions {
				if str.Color == "B" {
					blackScore += 1
				} else if str.Color == "W" {
					whiteScore += 1
				}
			}
		}

		stability := 520 - float64(totalEyes)/2 - float64(totalLiberties)*2 - float64(totalTerritory)/2
		if sekiDetected || snapBackDetected || stability < 100 {
			stability = 100
		}

		if stability == 100 {
			aliveGroups = append(aliveGroups, group)
		}
	}

	return blackScore, whiteScore
}
