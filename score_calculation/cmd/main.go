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
				exploreString(x, y, board, visited, stone, &str.Positions)
				strings = append(strings, str)
			}
		}
	}

	fmt.Println("Identified Strings and their positions:")
	for _, str := range strings {
		fmt.Println("String Color:", str.Color, "Positions:", str.Positions, "Length:", len(str.Positions))
	}

	// Group strings
	groups := groupStrings(strings, board)

	// Display grouped strings
	fmt.Println("Grouped Strings:")
	for idx, group := range groups {
		fmt.Printf("Group %d:\n", idx+1)
		for _, str := range group {
			fmt.Printf("Color: %s, Positions: %v, Length: %d\n", str.Color, str.Positions, len(str.Positions))
		}
	}
}

func exploreString(x, y int, board models.Board, visited [][]bool, color string, positions *[]models.Position) {
	directions := []models.Position{{0, 1}, {0, -1}, {1, 0}, {-1, 0}} // Right, Left, Down, Up
	stack := []models.Position{{X: x, Y: y}}

	for len(stack) > 0 {
		p := stack[len(stack)-1]
		stack = stack[:len(stack)-1]

		if visited[p.Y][p.X] {
			continue
		}

		visited[p.Y][p.X] = true
		*positions = append(*positions, p)

		for _, d := range directions {
			nx, ny := p.X+d.X, p.Y+d.Y
			if nx >= 0 && nx < len(board[0]) && ny >= 0 && ny < len(board) && board[ny][nx] == color && !visited[ny][nx] {
				stack = append(stack, models.Position{X: nx, Y: ny})
			}
		}
	}
}

func groupStrings(strings []models.String, board models.Board) [][]models.String {
	groups := [][]models.String{}
	used := make(map[int]bool)
	atariStrings := make(map[int]bool) // Track strings in Atari

	// First, identify strings in Atari
	for i, str := range strings {
		if countLiberties(str, board) == 1 { // This string is in Atari if it has exactly one liberty
			atariStrings[i] = true
		}
	}

	for i, str1 := range strings {
		if used[i] || atariStrings[i] {
			continue // Skip strings that are already grouped or in Atari
		}

		newGroup := []models.String{str1}
		used[i] = true

		for j, str2 := range strings {
			if i != j && !used[j] && !atariStrings[j] { // Check connectivity only if str2 is not in Atari
				full, half := canConnect(str1, str2, board)
				if full || half {
					newGroup = append(newGroup, str2)
					used[j] = true
				}
			}
		}
		groups = append(groups, newGroup)
	}

	return groups
}

func canConnect(str1, str2 models.String, board models.Board) (bool, bool) {
	// Scan all positions of str1 and check for direct adjacency or near adjacency (for potential half connections) with positions of str2
	fullConnection := false
	halfConnectionCount := 0
	for _, pos1 := range str1.Positions {
		for _, pos2 := range str2.Positions {
			// Check direct adjacency (common Go board moves: left, right, up, down)
			if (pos1.X == pos2.X && abs(pos1.Y-pos2.Y) == 1) || (pos1.Y == pos2.Y && abs(pos1.X-pos2.X) == 1) {
				if isEmptyBetween(pos1, pos2, board) {
					fullConnection = true
				}
			}
			// Check for half connections (could be diagonal or one space apart)
			if isPotentialHalfConnection(pos1, pos2, board) {
				halfConnectionCount++
			}
		}
	}
	// Consider at least two valid half connection points to count as potential connectability
	return fullConnection, halfConnectionCount >= 2
}

// isEmptyBetween checks if the position between two points is empty and thus a valid connection spot
func isEmptyBetween(pos1, pos2 models.Position, board models.Board) bool {
	// Calculate mid-point between two positions (if directly adjacent, this check is trivially true for full connections)
	midX := (pos1.X + pos2.X) / 2
	midY := (pos1.Y + pos2.Y) / 2
	return board[midX][midY] == "0"
}

// isPotentialHalfConnection determines if a half connection can be established based on empty spots and distance
func isPotentialHalfConnection(pos1, pos2 models.Position, board models.Board) bool {
	// Check if the positions are one space apart with an empty space between them
	dx := abs(pos1.X - pos2.X)
	dy := abs(pos1.Y - pos2.Y)
	if (dx == 2 && dy == 0) || (dy == 2 && dx == 0) {
		midX := (pos1.X + pos2.X) / 2
		midY := (pos1.Y + pos2.Y) / 2
		return board[midX][midY] == "0"
	}
	return false
}

func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

// countLiberties calculates the number of empty adjacent positions around a string
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

func isValidAndEmpty(board models.Board, x, y int) bool {
	return x >= 0 && x < len(board) && y >= 0 && y < len(board) && board[x][y] == "0"
}
