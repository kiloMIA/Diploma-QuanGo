import os
import imutils
import cv2 as cv
import numpy as np
from imutils.perspective import four_point_transform

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
    avg_color = avg_color[:3] 

    if np.mean(avg_color) < 127: 
        return "black"
    else:
        return "white"

def find_stones(warped_image):
    gray = cv.cvtColor(warped_image, cv.COLOR_BGR2GRAY)
    gray_blurred = cv.GaussianBlur(gray, (7, 7), 0)

    circles = cv.HoughCircles(gray_blurred, cv.HOUGH_GRADIENT, 1.2, 20,
                            param1=50, param2=30, minRadius=10, maxRadius=20)

    stones = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            stone_color = classify_stone_color(warped_image, x, y, r)
            stones.append((x, y, stone_color))

            cv.circle(warped_image, (x, y), r, (0, 255, 0), 4)
            cv.circle(warped_image, (x, y), 2, (255, 0, 0), -1)

    return warped_image, stones

def process_image(image_path, result_path):
    warped = find_board(image_path, result_path)
    if warped is not None:
        warped_with_stones, stones = find_stones(warped)
        cv.imwrite(os.path.join(result_path, "warped", os.path.basename(image_path)), warped_with_stones)
    else:
        print(f"Board not found in {image_path}")
def process_dataset(dataset_path, result_path):
    for file in os.listdir(dataset_path):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            process_image(os.path.join(dataset_path, file), result_path)

if __name__ == "__main__":
    dataset_path = "image"
    result_path = "result25012024"

    for folder in ["warped"]:
        os.makedirs(os.path.join(result_path, folder), exist_ok=True)

    process_dataset(dataset_path, result_path)