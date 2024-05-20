FROM golang:1.22.2 as builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o /go/bin/score_calculation cmd/main.go

FROM alpine:latest

WORKDIR /root/

COPY --from=builder /go/bin/score_calculation .

EXPOSE 50051

CMD ["./score_calculation"]

