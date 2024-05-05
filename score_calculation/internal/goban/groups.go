package goban

import "github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"

func ExploreString(x, y int, board models.Board, visited [][]bool, color string, positions *[]models.Position) {
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

func GroupStrings(strings []models.String, board models.Board) []models.Group {
	groups := []models.Group{}
	used := make(map[int]bool)
	atariStrings := make(map[int]bool)

	// Identify strings in Atari
	for i, str := range strings {
		if countLiberties(str, board) == 1 { // This string is in Atari if it has exactly one liberty
			atariStrings[i] = true
		}
	}

	for i, str1 := range strings {
		if used[i] || atariStrings[i] {
			continue // Skip strings that are already grouped or in Atari
		}

		newGroup := models.Group{Strings: []models.String{str1}}
		used[i] = true

		for j, str2 := range strings {
			if i != j && !used[j] && !atariStrings[j] { // Check connectivity only if str2 is not in Atari
				full, half := canConnect(str1, str2, board)
				if full || half {
					newGroup.Strings = append(newGroup.Strings, str2)
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
