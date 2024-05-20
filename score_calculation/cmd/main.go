package main

import (
	"context"
	"log"
	"net"

	"github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/models"
	"github.com/kiloMIA/Diploma-QuanGo/score_calculation/internal/rules"
	pb "github.com/kiloMIA/Diploma-QuanGo/score_calculation/proto"
	"google.golang.org/grpc"
)

const (
	port = ":50051"
)

type server struct {
	pb.UnimplementedBoardServiceServer
}

func (s *server) SendBoard(ctx context.Context, req *pb.BoardRequest) (*pb.ScoreReply, error) {
	board := models.Board{}
	for y := 0; y < int(req.Size); y++ {
		for x := 0; x < int(req.Size); x++ {
			board[y][x] = req.Board[y*int(req.Size)+x]
		}
	}

	blackScore, whiteScore := rules.CalculateScore(board, int(req.BlackPrisoners), int(req.WhitePrisoners), float64(req.Komi))
	winner := "Black"
	if whiteScore > blackScore {
		winner = "White"
	}

	return &pb.ScoreReply{
		BlackScore: float32(blackScore),
		WhiteScore: float32(whiteScore),
		Winner:     winner,
	}, nil
}

func main() {
	lis, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	pb.RegisterBoardServiceServer(s, &server{})
	log.Printf("server listening at %v", lis.Addr())
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
