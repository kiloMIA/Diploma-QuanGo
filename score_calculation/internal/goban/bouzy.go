package goban

const boardSize = 19

// InitializeInfluence initializes the board with influence values based on stone positions.
func InitializeInfluence(board [boardSize][boardSize]string) [boardSize][boardSize]int {
	influence := [boardSize][boardSize]int{}
	for y := 0; y < boardSize; y++ {
		for x := 0; x < boardSize; x++ {
			if board[y][x] == "B" {
				influence[y][x] = 64 // Positive high value for black
			} else if board[y][x] == "W" {
				influence[y][x] = -64 // Negative high value for white
			}
		}
	}
	return influence
}

// Dilation spreads influence across the board based on current positions and influence values.
func Dilation(board [boardSize][boardSize]string, influence *[boardSize][boardSize]int, steps int) {
	for step := 0; step < steps; step++ {
		tempInfluence := *influence
		for y := 0; y < boardSize; y++ {
			for x := 0; x < boardSize; x++ {
				spreadInfluence(x, y, board, &tempInfluence, (*influence)[y][x])
			}
		}
		*influence = tempInfluence
	}
}

// Erosion reduces influence based on the surrounding opposing or neutral influences.
func Erosion(influence *[boardSize][boardSize]int, steps int) {
	for step := 0; step < steps; step++ {
		tempInfluence := *influence
		for y := 0; y < boardSize; y++ {
			for x := 0; x < boardSize; x++ {
				if tempInfluence[y][x] != 0 {
					checkInfluenceRemoval(x, y, &tempInfluence, tempInfluence[y][x])
				}
			}
		}
		*influence = tempInfluence
	}
}

func spreadInfluence(x, y int, board [boardSize][boardSize]string, influence *[boardSize][boardSize]int, value int) {
	directions := [4][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}
	for _, d := range directions {
		nx, ny := x+d[0], y+d[1]
		if nx >= 0 && nx < boardSize && ny >= 0 && ny < boardSize && (board[ny][nx] == "0" || influence[ny][nx]*value >= 0) {
			influence[ny][nx] += value / 64 // Spread a fraction of the original value
		}
	}
}

func checkInfluenceRemoval(x, y int, influence *[boardSize][boardSize]int, value int) {
	directions := [4][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}
	countOpposite, countSame := 0, 0

	for _, d := range directions {
		nx, ny := x+d[0], y+d[1]
		if nx >= 0 && nx < boardSize && ny >= 0 && ny < boardSize {
			neighborValue := (*influence)[ny][nx]
			if neighborValue*value < 0 {
				countOpposite++
			} else if neighborValue*value > 0 {
				countSame++
			}
		}
	}

	if countOpposite > countSame { // Only erase if surrounded mostly by opposite influence
		(*influence)[y][x] = 0
	}
}
