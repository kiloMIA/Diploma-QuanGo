package goban

import (
	"github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"
)

func CheckForSeki(groups []models.Group, board models.Board) bool {
	for _, group := range groups {
		for i := 0; i < len(group.Strings); i++ {
			for j := i + 1; j < len(group.Strings); j++ {
				if isPotentialSeki(group.Strings[i], group.Strings[j], board) {
					return true
				}
			}
		}
	}
	return false
}

func isPotentialSeki(str1, str2 models.String, board models.Board) bool {
	if len(str1.Positions) < 3 || len(str2.Positions) < 3 {
		return false
	}

	lib1 := GetLiberties(str1, board)
	lib2 := GetLiberties(str2, board)

	sharedLiberties := 0
	for lib := range lib1 {
		if _, exists := lib2[lib]; exists {
			sharedLiberties++
		}
	}

	return sharedLiberties >= 2 && sharedLiberties <= 4
}
