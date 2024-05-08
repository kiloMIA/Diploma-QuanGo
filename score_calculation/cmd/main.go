package main

import (
	"fmt"
	"github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/goban"
	"github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"
	"github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/sgf"
)

func main() {
	board, result := sgf.ParseSGF("/home/kilo/projects/Diploma-QuanGo/score_calculation/sgf_tests/scored-games/001_001.sgf")
	fmt.Println("Final Board State:")
	for _, row := range board {
		fmt.Println(row)
	}
	fmt.Println("Result:", result)

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

	fmt.Println("Grouped Strings:")
	var aliveGroups []models.Group
	for idx, group := range groups {
		totalEyes, totalLiberties, totalTerritory := 0, 0, 0
		sekiDetected := goban.CheckForSeki([]models.Group{group}, board)
		snapBackDetected := false

		for i := 0; i < len(group.Strings)-1; i++ {
			for j := i + 1; j < len(group.Strings); j++ {
				if goban.CheckForSnapBack(group.Strings[i], group.Strings[j], board) {
					snapBackDetected = true
					fmt.Printf("Snapback detected between strings at indices %d and %d\n", i, j)
				}
			}
		}

		for _, str := range group.Strings {
			actualEyes, _, _ := goban.IdentifyEyesAndEyelikes(str, board)
			libertyValue := goban.EvaluateLibertyValue(str, board)
			totalEyes += actualEyes
			totalLiberties += int(libertyValue)
			for _, pos := range str.Positions {
				totalTerritory += influence[pos.Y][pos.X]
			}
		}

		stability := 520 - float64(totalEyes)/2 - float64(totalLiberties)*2 - float64(totalTerritory)/2
		if sekiDetected || snapBackDetected || stability < 100 {
			stability = 100
		}

		fmt.Printf("Group %d: Stability: %.2f, Territory: %d, Eyes: %d, Liberties: %d\n", idx+1, stability, totalTerritory, totalEyes, totalLiberties)
		if stability == 100 {
			aliveGroups = append(aliveGroups, group)
		}
	}

	fmt.Println("Final Influence Map after Dilation and Erosion:")
	for _, line := range influence {
		fmt.Println(line)
	}

	fmt.Println("Surviving Groups After Stability Checks:")
	for idx, group := range aliveGroups {
		fmt.Printf("Group %d: Survived\n", idx+1)
		fmt.Print("Group: ", group)
	}
}
