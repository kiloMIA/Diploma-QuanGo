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

	// Display grouped strings
	fmt.Println("Grouped Strings:")
	for idx, group := range groups {
		fmt.Printf("Group %d:\n", idx+1)
		for _, str := range group {
			fmt.Printf("Color: %s, Positions: %v, Length: %d\n", str.Color, str.Positions, len(str.Positions))
		}
	}
}
