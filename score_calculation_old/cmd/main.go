package main

import (
	"context"
	"fmt"
	"log"
	"net"

	"google.golang.org/grpc"
    proto "github.com/kiloMIA/Diploma-QuanGo/score_calculation"
)

const (
    Empty = iota
    Black
    White
)

type Board struct {
    grid [][]int
}

type server struct {
    proto.UnimplementedBoardServiceServer
}

func (s *server) SendBoard(ctx context.Context, req *proto.BoardRequest) (*proto.ScoreReply, error) {
    boardSize := int(req.Size)
    board := NewBoard(boardSize) 

    for i, val := range req.Board {
        x := i / boardSize
        y := i % boardSize
        switch val {
        case 0:
        case 1:
            board.SetStone(x, y, Black)
        case 2:
            board.SetStone(x, y, White)
        }
    }

    // Calculate and log the score
    blackScore, whiteScore := board.CalculateScore(7.5)
    fmt.Printf("Black: %.1f, White: %.1f\n", blackScore, whiteScore)

    // Since the Python client doesn't need a response, return an empty reply
    return &proto.ScoreReply{}, nil
}

// NewBoard creates a new board with the given size.
func NewBoard(size int) *Board {
    grid := make([][]int, size)
    for i := range grid {
        grid[i] = make([]int, size)
    }
    return &Board{grid: grid}
}

// SetStone sets a stone on the board.
func (b *Board) SetStone(x, y, color int) {
    b.grid[x][y] = color
}

// CalculateScore calculates and returns the score according to Chinese rules.
func (b *Board) CalculateScore(komi float64) (float64, float64) {
    blackScore, whiteScore := 0.0, komi
    visited := make([][]bool, len(b.grid))
    for i := range visited {
        visited[i] = make([]bool, len(b.grid))
    }

    for x, row := range b.grid {
        for y, cell := range row {
            if cell == Black {
                blackScore++
            } else if cell == White {
                whiteScore++
            } else if !visited[x][y] {
                territory, isSingleColor := b.checkTerritory(x, y, visited)
                if isSingleColor {
                    if territory == Black {
                        blackScore++
                    } else if territory == White {
                        whiteScore++
                    }
                }
            }
        }
    }

    return blackScore, whiteScore
}

// checkTerritory is a helper function to determine the owner of a territory.
func (b *Board) checkTerritory(x, y int, visited [][]bool) (int, bool) {
    if x < 0 || y < 0 || x >= len(b.grid) || y >= len(b.grid) || visited[x][y] {
        return 0, true
    }

    if b.grid[x][y] != Empty {
        return b.grid[x][y], true
    }

    visited[x][y] = true
    territoryColor := 0
    isSingleColor := true

    directions := [][]int{{-1, 0}, {1, 0}, {0, -1}, {0, 1}}
    for _, d := range directions {
        dx, dy := x+d[0], y+d[1]
        color, singleColor := b.checkTerritory(dx, dy, visited)

        if territoryColor == 0 {
            territoryColor = color
        } else if color != territoryColor {
            isSingleColor = false
        }

        isSingleColor = isSingleColor && singleColor
    }

    return territoryColor, isSingleColor
}

func main() {
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatalf("Failed to listen: %v", err)
    }
    s := grpc.NewServer()
    proto.RegisterBoardServiceServer(s, &server{})
    log.Println("Server listening on :50051")
    if err := s.Serve(lis); err != nil {
        log.Fatalf("Failed to serve: %v", err)
    }
}