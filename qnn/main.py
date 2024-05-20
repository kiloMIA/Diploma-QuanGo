from fastapi import FastAPI, File, UploadFile
import grpc
import board_pb2 as pb2
import board_pb2_grpc as pb2_grpc
from PIL import Image
import torch
from torchvision import transforms
from goban_model import StoneClassifierCNN
import numpy as np

app = FastAPI()

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]

model = StoneClassifierCNN().to(DEVICE)
model.load_state_dict(torch.load("output/detector.pth", map_location=DEVICE))
model.eval()


def preprocess_image(image):
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=MEAN, std=STD),
        ]
    )
    image = Image.open(image).convert("RGB")
    return transform(image).unsqueeze(0)


def decode_predictions(preds):
    board = preds.argmax(1).cpu().numpy().reshape(19, 19)
    char_board = np.full(board.shape, ".", dtype=str)
    char_board[board == 0] = "."
    char_board[board == 1] = "B"
    char_board[board == 2] = "W"
    return char_board


async def send_to_go_backend(board, black_prisoners, white_prisoners, komi):
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = pb2_grpc.BoardServiceStub(channel)
        board_list = board.flatten().tolist()
        request = pb2.BoardRequest(
            board=board_list,
            size=19,
            black_prisoners=black_prisoners,
            white_prisoners=white_prisoners,
            komi=komi,
        )
        response = await stub.SendBoard(request)
        return response


@app.post("/process-image/")
async def process_image(
    image: UploadFile = File(...),
    black_prisoners: int = 0,
    white_prisoners: int = 0,
    komi: float = 6.5,
):
    image = preprocess_image(image.file).to(DEVICE)

    with torch.no_grad():
        preds = model(image)

    board_state = decode_predictions(preds)

    response = await send_to_go_backend(
        board_state, black_prisoners, white_prisoners, komi
    )

    return {
        "black_score": response.black_score,
        "white_score": response.white_score,
        "winner": response.winner,
    }
