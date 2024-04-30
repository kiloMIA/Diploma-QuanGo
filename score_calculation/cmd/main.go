package main

import (
	"fmt"

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

  strings := make([][]models.Position, 0)
  visited := make([][]bool, len(board))
	for i := range visited {
		visited[i] = make([]bool, len(board[i]))
	}

  for y, row := range board {
		for x, stone := range row {
			if stone != "0" && !visited[y][x] {
				string := make([]models.Position, 0) // to hold positions of the current string
				exploreString(x, y, board, visited, stone, &string)
				strings = append(strings, string) // Add the completed string
			}
		}
	}

	fmt.Println("Strings and their positions:")
	for _, string := range strings {
		fmt.Println("String at positions:", string, "Length:", len(string))
	}

}
func exploreString(x, y int, board models.Board, visited [][]bool, color string, string *[]models.Position) {
	directions := []models.Position{{0, 1}, {0, -1}, {1, 0}, {-1, 0}} // Right, Left, Down, Top
	stack := []models.Position{{X: x, Y: y}}

	for len(stack) > 0 {
		p := stack[len(stack)-1]
		stack = stack[:len(stack)-1]

		if visited[p.Y][p.X] {
			continue
		}

		visited[p.Y][p.X] = true
		*string = append(*string, p) 

		for _, d := range directions {
			nx, ny := p.X+d.X, p.Y+d.Y
			if nx >= 0 && nx < len(board[0]) && ny >= 0 && ny < len(board) && board[ny][nx] == color && !visited[ny][nx] {
				stack = append(stack, models.Position{X: nx, Y: ny})
			}
		}
	}
}
