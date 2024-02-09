import os
import imutils
import cv2 as cv
import numpy as np
import grpc
from imutils.perspective import four_point_transform
import board_pb2
import board_pb2_grpc

def send_board_state(board):
    flattened_board = [cell for row in board for cell in row]
    board_size = len(board)
    with grpc.insecure_channel('score_calculation:50051') as channel:
        stub = board_pb2_grpc.BoardServiceStub(channel)
        stub.SendBoard(board_pb2.BoardRequest(board=flattened_board, size=board_size))
        print("Board state sent to Go service for score calculation.")

def remove_duplicates_and_close_lines(lines, threshold=10):
    if not lines:
        return []
    lines = sorted(lines, key=lambda line: line[0])
    clusters = [[lines[0]]]
    for current_line in lines[1:]:
        placed = False
        for cluster in clusters:
            if abs(cluster[-1][0] - current_line[0]) < threshold:
                cluster.append(current_line)
                placed = True
                break
        if not placed:
            clusters.append([current_line])
    averaged_lines = []
    for cluster in clusters:
        avg_rho = np.mean([line[0] for line in cluster])
        avg_theta = np.mean([line[1] for line in cluster])
        averaged_lines.append((avg_rho, avg_theta))
    return averaged_lines

def detect_board_lines(warped_image):
    gray = cv.cvtColor(warped_image, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray, 50, 150, apertureSize=3)
    lines = cv.HoughLines(edges, 1, np.pi / 180, 150)
    if lines is None:
        return [], [], (0, 0, 0, 0), (0, 0)  

    vertical_lines, horizontal_lines = [], []
    for line in lines:
        rho, theta = line[0]
        if theta < np.pi / 4 or theta > 3 * np.pi / 4:
            vertical_lines.append((rho, theta))
        else:
            horizontal_lines.append((rho, theta))

    vertical_lines = remove_duplicates_and_close_lines(vertical_lines)
    horizontal_lines = remove_duplicates_and_close_lines(horizontal_lines)
    board_edges, board_size = calculate_board_properties(vertical_lines, horizontal_lines)
    return vertical_lines, horizontal_lines, board_edges, board_size

def calculate_board_properties(vertical_lines, horizontal_lines):
    if not vertical_lines or not horizontal_lines:
        return (0, 0, 0, 0), (0, 0)  # Default values if no lines are detected

    min_v = min(vertical_lines, key=lambda x: x[0])[0]
    max_v = max(vertical_lines, key=lambda x: x[0])[0]
    min_h = min(horizontal_lines, key=lambda x: x[0])[0]
    max_h = max(horizontal_lines, key=lambda x: x[0])[0]

    board_edges = (min_v, max_v, min_h, max_h)
    board_size = (len(vertical_lines), len(horizontal_lines))

    return board_edges, board_size

def find_board(image_path, save_path):
    image = cv.imread(image_path)
    orig = image.copy()
    ratio = image.shape[0] / 500.0
    image = imutils.resize(image, height=500)

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    gray = cv.GaussianBlur(gray, (5, 5), 0)
    edged = cv.Canny(gray, 50, 255)

    cnts, hierarchy = cv.findContours(edged.copy(), cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv.contourArea, reverse=True)[:5]
    screenCnt = None

    for c in cnts:
        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is None:
        print("No rectangular contour found")
        return None, edged, None  
    else:
        warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
        return warped, edged, screenCnt  

def classify_stone_color(image, x, y, r):
    x1, y1, x2, y2 = max(0, x-r), max(0, y-r), min(image.shape[1], x+r), min(image.shape[0], y+r)
    roi = image[y1:y2, x1:x2]
    if roi.size == 0:
        return "unknown"

    avg_color_per_row = np.average(roi, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    

    if np.isscalar(avg_color):
        avg_color = np.array([avg_color] * 3) 

    if np.mean(avg_color[:3]) < 127:  
        return "black"
    else:
        return "white"

def apply_advanced_filters(image):
    shifted = cv.pyrMeanShiftFiltering(image, sp=21, sr=51)
    gray = cv.cvtColor(shifted, cv.COLOR_BGR2GRAY)
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalized = clahe.apply(gray)

    _, thresholded = cv.threshold(equalized, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    dilated = cv.dilate(thresholded, None, iterations=1)
    eroded = cv.erode(dilated, None, iterations=1)

    blurred = cv.GaussianBlur(eroded, (7, 7), 0)
    return blurred

def detect_stones_with_filters(warped_image, min_radius=10, max_radius=20, param1=50, param2=30):
    filtered_image = apply_advanced_filters(warped_image)
    circles = cv.HoughCircles(filtered_image, cv.HOUGH_GRADIENT, dp=1.2, minDist=20,
                            param1=param1, param2=param2, minRadius=min_radius, maxRadius=max_radius)
    stones = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            stone_color = classify_stone_color(warped_image, x, y, r) 
            stones.append((x, y, r, stone_color))
            cv.circle(warped_image, (x, y), r, (0, 255, 0), 4)
            cv.circle(warped_image, (x, y), 2, (255, 0, 0), -1)

    stones = eliminate_duplicate_stones(stones)
    return warped_image, stones

def eliminate_duplicate_stones(stones):
    unique_stones = []
    stone_positions = {}

    for stone in stones:
        x, y, r, color = stone
        pos_key = (x, y)

        if pos_key in stone_positions:
            existing_stone = stone_positions[pos_key]
            if existing_stone[3] != color:
                if existing_stone[2] < r:
                    stone_positions[pos_key] = stone
                    unique_stones = [s for s in unique_stones if (s[0], s[1]) != pos_key]
                    unique_stones.append(stone)
            elif existing_stone[2] < r:
                stone_positions[pos_key] = stone
                unique_stones = [s for s in unique_stones if (s[0], s[1]) != pos_key]
                unique_stones.append(stone)
        else:
            stone_positions[pos_key] = stone
            unique_stones.append(stone)

    return unique_stones

def map_stones_to_grid(stones, board_size=(19, 19), image_dim=(500, 500)):
    board = [[0 for _ in range(board_size[1])] for _ in range(board_size[0])]
    cell_width = image_dim[0] / (board_size[1] - 1)
    cell_height = image_dim[1] / (board_size[0] - 1)

    for x, y, color in stones:
        grid_x = round(x / cell_width)
        grid_y = round(y / cell_height)
        
        board[grid_y][grid_x] = 1 if color == 'black' else 2

    return board

def convert_pixel_to_grid(x, y, image_dim, board_size=(19, 19)):
    if board_size[0] <= 1 or board_size[1] <= 1:
        print("Invalid board size detected. Defaulting to standard 19x19 board.")
        board_size = (19, 19)

    cell_width = image_dim[0] / (board_size[1] - 1)
    cell_height = image_dim[1] / (board_size[0] - 1)
    
    grid_x = round(x / cell_width)
    grid_y = round(y / cell_height)
    return grid_x, grid_y

def populate_board(stones, image_dim, board_size=(19, 19)):
    if image_dim[0] == 0 or image_dim[1] == 0:
        print("Invalid image dimensions. Skipping board population.")
        return [[0 for _ in range(board_size[1])] for _ in range(board_size[0])]

    board = [[0 for _ in range(board_size[1])] for _ in range(board_size[0])]
    for x, y, r, color in stones:
        grid_x, grid_y = convert_pixel_to_grid(x, y, image_dim, board_size)
        if 0 <= grid_x < board_size[1] and 0 <= grid_y < board_size[0]:
            board[grid_y][grid_x] = 1 if color == 'black' else 2
    return board

def process_image(image_path, result_path):
    # Ensure necessary directories exist
    for subfolder in ["edged", "outline", "warped", "final_image"]:
        os.makedirs(os.path.join(result_path, subfolder), exist_ok=True)

    warped, edged, outline = find_board(image_path, result_path)
    if warped is not None:
        # Save edged image
        cv.imwrite(os.path.join(result_path, "edged", os.path.basename(image_path)), edged)

        # Draw outline and save
        outline_img = cv.drawContours(cv.imread(image_path).copy(), [outline], -1, (0, 255, 0), 3)
        cv.imwrite(os.path.join(result_path, "outline", os.path.basename(image_path)), outline_img)

        # Save warped image
        cv.imwrite(os.path.join(result_path, "warped", os.path.basename(image_path)), warped)

        # Process stones detection
        vertical_lines, horizontal_lines, board_edges, board_size = detect_board_lines(warped)
        final_image, stones = detect_stones_with_filters(warped)

        # Save final image with stones detected
        cv.imwrite(os.path.join(result_path, "final_image", os.path.basename(image_path)), final_image)
        board_array = populate_board(stones, warped.shape[:2], board_size)
        print("Board Array:")
        for row in board_array:
            print(row)
        board_array = populate_board(stones, warped.shape[:2], board_size)
        send_board_state(board_array)
    else:
        print(f"Board not found in {image_path}")

def process_dataset(dataset_path, result_path):
    for file in os.listdir(dataset_path):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            process_image(os.path.join(dataset_path, file), result_path)

if __name__ == "__main__":
    dataset_path = "image"
    result_path = "result09022024"
    for folder in ["warped"]:
        os.makedirs(os.path.join(result_path, folder), exist_ok=True)
    process_dataset(dataset_path, result_path)

