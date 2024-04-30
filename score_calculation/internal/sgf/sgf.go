package sgf

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"
)


func initializeBoard() models.Board {
	var board models.Board
	for i := range board {
		for j := range board[i] {
			board[i][j] = "0" // Empty point
		}
	}
	return board
}

func applyMove(board models.Board, move string, player string) models.Board {
	newBoard := board
	if len(move) == 2 {
		col := int(move[0] - 'a') // convert letter to index
		row := int(move[1] - 'a') // convert number to index
		if col >= 0 && col < 19 && row >= 0 && row < 19 {
			newBoard[row][col] = player
		}
	}
	return newBoard
}

func ParseSGF(filename string) (models.Board, string) {
	file, err := os.Open(filename)
	if err != nil {
		panic(err)
	}
	defer file.Close()

	board := initializeBoard()
	var moves []string
	var result string

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, ";B[") || strings.HasPrefix(line, ";W[") {
			move := line[3:5]
			player := "B"
			if strings.HasPrefix(line, ";W[") {
				player = "W"
			}
			moves = append(moves, fmt.Sprintf("%s plays at %s", player, move))
			board = applyMove(board, move, player)
		} else if strings.HasPrefix(line, "RE[") {
			result = line[3 : len(line)-1]
		}
	}

	return board, result
}
