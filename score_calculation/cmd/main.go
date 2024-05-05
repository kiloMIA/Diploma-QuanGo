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
	fmt.Println("Identified Strings and their positions:")
	for _, str := range strings {
		fmt.Println("String Color:", str.Color, "Positions:", str.Positions, "Length:", len(str.Positions))
	}

	// Evaluate strings for eyes and liberties
	for _, str := range strings {
		actualEyes, specialEyes, eyelikes := goban.IdentifyEyesAndEyelikes(str, board)
		libertyValue := goban.EvaluateLibertyValue(str, board)
		fmt.Printf("String Color: %s, Liberties Value: %.2f, Actual Eyes: %d, Special Eyes: %d, Eyelikes: %d, Positions: %v, Length: %d\n",
			str.Color, libertyValue, actualEyes, specialEyes, eyelikes, str.Positions, len(str.Positions))
	}

	// Group strings
	groups := goban.GroupStrings(strings, board)

	// Using Bouzy Algorithm
	influence := goban.Dilation(board, 8)
	goban.Erosion(&influence, 21)
	// Calculating stability of groups
	for idx, group := range groups {
		totalEyes, totalLiberties, totalTerritory := 0, 0, 0
		sekiDetected := goban.CheckForSeki([][]models.String{group.Strings}, board)
		snapBackDetected := false

		for _, str := range group.Strings {
			actualEyes, _, _ := goban.IdentifyEyesAndEyelikes(str, board)
			libertyValue := goban.EvaluateLibertyValue(str, board)
			totalEyes += actualEyes
			totalLiberties += int(libertyValue)
			for _, pos := range str.Positions {
				if goban.CheckForSnapBack(pos, board, str.Color) {
					snapBackDetected = true
					fmt.Printf("Snapback detected at position: %v for color %s\n", pos, str.Color)
				}
				totalTerritory += influence[pos.Y][pos.X]
			}
		}

		stability := 520 - float64(totalEyes)/2 - float64(totalLiberties)*2 - float64(totalTerritory)/2
		if sekiDetected || snapBackDetected || stability < 100 {
			stability = 100
			fmt.Println("Stability set to 100 due to Seki or Snapback")
		}

		groups[idx].Stability = stability
		fmt.Printf("Group %d: Stability: %.2f, Territory: %d, Eyes: %d, Liberties: %d\n", idx+1, stability, totalTerritory, totalEyes, totalLiberties)
	}
	// Remove the deadest groups based on stability
	var aliveGroups []models.Group
	for _, group := range groups {
		if group.Stability <= 100 {
			aliveGroups = append(aliveGroups, group)
		}
	}

	fmt.Println("Surviving Groups After Stability Checks:")
	for idx, group := range aliveGroups {
		fmt.Printf("Group %d: Stability: %.2f, Territory: %d, Eyes: %d, Liberties: %d\n", idx+1, group.Stability, group.Territory, group.Eyes, group.Liberties)
	}
}
