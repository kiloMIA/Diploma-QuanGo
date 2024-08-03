QuanGo - is a system that automatically scores end game of the game of Go. Watch the demo here - [DEMO](https://youtu.be/q-ro1xduwbM?si=kisFHCjHIcphq8ay)

It consists of two modules:
QNN - Neural Network written in Pytorch, it identifies a board from a picture

Score Calculation Backend - Implementation of static algorithm developed by Andrea Carta in Golang, original article can be accesed [here](https://www.uni-trier.de/fileadmin/fb4/prof/BWL/FIN/Veranstaltungen/A_static_method_for_computing_the_score_of_a_Go_game__Carta_.pdf)

On this image you can see the architecture of the project
![Project_Architecture(1)](https://github.com/user-attachments/assets/5844522b-f288-4b1c-93c6-41fd155ce823)

Here is example board and example result
![Zrzut ekranu 2020-04-28 o 10 27 37](https://github.com/user-attachments/assets/d6a7d272-0e6b-4f0f-855f-4f844df27960)

Red color represents influence of white stones, while blue represents influence of black stones
![image_2024-06-12_10-48-32](https://github.com/user-attachments/assets/e20cef20-9a9d-469e-8aa0-fec9cf11b2bf)

QNN and Score Calculation Backend communicate through gRPC
```sh
message BoardRequest {
  repeated string board = 1; 
  int32 size = 2;            
  int32 black_prisoners = 3; 
  int32 white_prisoners = 4; 
  float komi = 5;            
}

message ScoreReply {
  float black_score = 1;
  float white_score = 2;
  string winner = 3;
}
```
