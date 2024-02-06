import os
import imutils
import cv2 as cv
import numpy as np
from imutils.perspective import four_point_transform

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
        return [], []
    vertical_lines, horizontal_lines = [], []
    for line in lines:
        for rho, theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            if theta < np.pi / 4 or theta > 3 * np.pi / 4:
                vertical_lines.append((rho, theta))
            else:
                horizontal_lines.append((rho, theta))
    vertical_lines = remove_duplicates_and_close_lines(vertical_lines)
    horizontal_lines = remove_duplicates_and_close_lines(horizontal_lines)
    return vertical_lines, horizontal_lines

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
        return None
    else:
        warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
        return warped

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
    b, g, r = cv.split(image)
    shifted = cv.pyrMeanShiftFiltering(image, sp=21, sr=51)
    gray = cv.cvtColor(shifted, cv.COLOR_BGR2GRAY)
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalized = clahe.apply(gray)

    blurred = cv.GaussianBlur(equalized, (7, 7), 0)
    return blurred

def detect_stones_with_filters(warped_image, min_radius=10, max_radius=20, param1=50, param2=30):
    filtered_image = apply_advanced_filters(warped_image)

    circles = cv.HoughCircles(filtered_image, cv.HOUGH_GRADIENT, dp=1.2, minDist=20,
                            param1=param1, param2=param2, minRadius=min_radius, maxRadius=max_radius)
    stones = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            stone_color = classify_stone_color(filtered_image, x, y, r)
            stones.append((x, y, r, stone_color))
            cv.circle(warped_image, (x, y), r, (0, 255, 0), 4)
            cv.circle(warped_image, (x, y), 2, (255, 0, 0), -1)
    return warped_image, stones

def process_image(image_path, result_path):
    warped = find_board(image_path, result_path)
    if warped is not None:
        vertical_lines, horizontal_lines = detect_board_lines(warped)
        warped_with_stones, stones = detect_stones_with_filters(warped)
        cv.imwrite(os.path.join(result_path, "warped", os.path.basename(image_path)), warped_with_stones)
    else:
        print(f"Board not found in {image_path}")

def process_dataset(dataset_path, result_path):
    for file in os.listdir(dataset_path):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            process_image(os.path.join(dataset_path, file), result_path)

if __name__ == "__main__":
    dataset_path = "image"
    result_path = "result06022024"
    for folder in ["warped"]:
        os.makedirs(os.path.join(result_path, folder), exist_ok=True)
    process_dataset(dataset_path, result_path)
