import os
import imutils
import cv2 as cv
from imutils.perspective import four_point_transform
from skimage.filters import threshold_local

def find_board(image_path, save_path):
    image = cv.imread(image_path)
    ratio = image.shape[0] / 500.0
    orig = image.copy()
    image = imutils.resize(image, height=500)

    # Save the original resized image
    cv.imwrite(os.path.join(save_path, "image", os.path.basename(image_path)), image)

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    gray = cv.GaussianBlur(gray, (5, 5), 0)
    edged = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)

    # Save the edged image
    cv.imwrite(os.path.join(save_path, "edged", os.path.basename(image_path)), edged)

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
    else:
        cv.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)

        # Save the image with outline
        cv.imwrite(os.path.join(save_path, "outline", os.path.basename(image_path)), image)

        warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
        warped = cv.cvtColor(warped, cv.COLOR_BGR2GRAY)
        T = threshold_local(warped, 11, offset=10, method="gaussian")
        warped = (warped > T).astype("uint8") * 255

        # Save the warped image
        cv.imwrite(os.path.join(save_path, "warped", os.path.basename(image_path)), warped)

def find_stones(warped_image):
    ret, thresh = cv.threshold(warped_image, 128, 255, cv.THRESH_BINARY)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    stones = []
    for c in contours:
        if is_stone_shape(c):
            M = cv.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                stones.append((cX, cY))
                if thresh[cY, cX] == 255:
                    stone_color = "white"
                else:
                    stone_color = "black"

                cv.drawContours(warped_image, [c], -1, (0, 255, 0), 2)
                cv.circle(warped_image, (cX, cY), 7, (255, 255, 255), -1)

    return warped_image, stones

def is_stone_shape(contour):
    pass

def process_dataset(dataset_path, result_path):
    for file in os.listdir(dataset_path):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            find_board(os.path.join(dataset_path, file), result_path)

if __name__ == "__main__":
    dataset_path = "image"
    result_path = "result"

    for folder in ["image", "edged", "outline", "warped"]:
        os.makedirs(os.path.join(result_path, folder), exist_ok=True)

    process_dataset(dataset_path, result_path)