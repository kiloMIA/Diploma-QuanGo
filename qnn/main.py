from datetime import datetime
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import Response
from PIL import Image
from starlette.responses import JSONResponse
import grpc
import io
import logging
import matplotlib.pyplot as plt
import numpy as np
import torch
from torchvision import transforms
from goban_model import StoneClassifierCNN
from bouzy import initialize_influence, erosion, dilation
import board_pb2 as pb2
import board_pb2_grpc as pb2_grpc

app = FastAPI()

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]

model = StoneClassifierCNN().to(DEVICE)
model.load_state_dict(torch.load("output/detector.pth", map_location=DEVICE))
model.eval()

logging.basicConfig(level=logging.INFO)


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


def plot_influence_map(influence_map):
    normalized_influence = np.abs(influence_map) / np.max(np.abs(influence_map))

    influence_image = np.zeros((influence_map.shape[0], influence_map.shape[1], 3))
    influence_image[:, :, 2] = (influence_map > 0) * normalized_influence
    influence_image[:, :, 0] = (influence_map < 0) * normalized_influence

    plt.figure(figsize=(8, 8))
    plt.imshow(influence_image, interpolation="nearest")
    plt.title("Influence Map")
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf


async def send_to_go_backend(board, black_prisoners, white_prisoners, komi):
    async with grpc.aio.insecure_channel("go-service:50051") as channel:
        stub = pb2_grpc.BoardServiceStub(channel)
        board_list = board.flatten().tolist()
        request = pb2.BoardRequest(
            board=board_list,
            size=19,
            black_prisoners=black_prisoners,
            white_prisoners=white_prisoners,
            komi=komi,
        )
        logging.info(f"Sending board to Go backend:\n{board}")
        response = await stub.SendBoard(request)
        return response


@app.post("/process-image/")
async def process_image(
    image: UploadFile = File(...),
    black_prisoners: int = Form(default=0),
    white_prisoners: int = Form(default=0),
    komi: float = Form(default=6.5),
):
    logging.info(
        f"Received black_prisoners: {black_prisoners}, white_prisoners: {white_prisoners}, komi: {komi}"
    )
    image_data = preprocess_image(image.file).to(DEVICE)

    with torch.no_grad():
        preds = model(image_data)

    board_state = decode_predictions(preds)
    logging.info(f"Decoded board state:\n{board_state}")

    response = await send_to_go_backend(
        board_state, black_prisoners, white_prisoners, komi
    )

    logging.info(f"Received response: {response}")

    influence = initialize_influence(board_state)
    dilation(board_state, influence, 8)
    erosion(influence, 21)
    image_buf = plot_influence_map(influence)

    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.filename}"

    json_response = {
        "black_score": response.black_score,
        "white_score": response.white_score,
        "winner": response.winner,
    }

    return Response(
        content=(
            b"--myboundary\r\n"
            b'Content-Disposition: form-data; name="json"\r\n'
            b"Content-Type: application/json\r\n\r\n"
            + JSONResponse(content=json_response).body
            + b"\r\n--myboundary\r\n"
            b'Content-Disposition: form-data; name="image"; filename="'
            + unique_filename.encode()
            + b'"\r\n'
            b"Content-Type: image/png\r\n\r\n"
            + image_buf.getvalue()
            + b"\r\n--myboundary--\r\n"
        ),
        media_type="multipart/form-data; boundary=myboundary",
    )
