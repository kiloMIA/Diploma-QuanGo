package goban

import "github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"

func checkForForcedConnections(board *models.Board, groups []models.Group, damePoints []models.Position) []models.Position {
    var forcedConnections []models.Position
    for _, point := range damePoints {
        simulateFill(board, point, "B")
        if affectsGroupStatus(groups, *board) {
            forcedConnections = append(forcedConnections, point)
        }
        (*board)[point.Y][point.X] = "0"

        simulateFill(board, point, "W")
        if affectsGroupStatus(groups, *board) {
            forcedConnections = append(forcedConnections, point)
        }
        (*board)[point.Y][point.X] = "0"
    }
    return forcedConnections
}

func simulateFill(board *models.Board, point models.Position, color string) {
    original := (*board)[point.Y][point.X]
    if original == "0" {
        (*board)[point.Y][point.X] = color
    }
}

func affectsGroupStatus(groups []models.Group, board models.Board) bool {
    return false
}

