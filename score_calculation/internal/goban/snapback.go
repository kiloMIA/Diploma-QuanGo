package goban

import (
    "github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"
)

// CheckForSnapBack adjusts for shared single liberty and mutual capture threat.
func CheckForSnapBack(str1, str2 models.String, board models.Board) bool {
    if len(GetLiberties(str1, board)) != 1 || len(GetLiberties(str2, board)) != 1 {
        return false
    }

    sharedLiberty := findSharedLiberty(str1, str2, board)
    if sharedLiberty != (models.Position{}) && bothInAtariAfterCapture(str1, str2, sharedLiberty, board) {
        return true
    }

    return false
}

func findSharedLiberty(str1, str2 models.String, board models.Board) models.Position {
    lib1 := GetLiberties(str1, board)
    for lib := range lib1 {
        if _, exists := GetLiberties(str2, board)[lib]; exists {
            return lib
        }
    }
    return models.Position{} // Return an empty position if no shared liberty
}

func bothInAtariAfterCapture(str1, str2 models.String, liberty models.Position, board models.Board) bool {
    // Simulate capture of str1
    board[liberty.Y][liberty.X] = str2.Color
    if IsStoneInAtari(liberty, board, str2.Color) {
        // Simulate capture of str2
        board[liberty.Y][liberty.X] = str1.Color
        if IsStoneInAtari(liberty, board, str1.Color) {
            return true
        }
    }
    return false
}

