import cv2
import numpy as np
import utils

def find_board(image):
    imgContours = image.copy()
    imgBiggestContour = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 1)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 13, 5)
    edges = utils.auto_canny(thresh)
    cv2.imshow("edges", edges)
    cv2.waitKey(0)

    kernel = np.ones((5,5))
    imgDial = cv2.dilate(edges, kernel, 2)
    cv2.imshow("dilate", imgDial)
    cv2.waitKey(0)
    imgErode = cv2.erode(imgDial, kernel, 1)
    cv2.imshow("erod", imgErode)
    cv2.waitKey(0)

    contours, hierarchy = cv2.findContours(imgErode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)
    cv2.imshow("contour", imgContours)
    cv2.waitKey(0)
    
    biggest, maxArea = biggestContour(contours)
    if biggest.size != 0:
        biggest = reorder(biggest)
        cv2.drawContours(imgBiggestContour, biggest, -1, (0, 255, 0), 20)
        heightImg = imgBiggestContour.shape[0]
        widthImg = imgBiggestContour.shape[1]
        cv2.imshow("biggest", imgBiggestContour)
        cv2.waitKey(0)
        imgBiggestContour = drawRectangle(imgBiggestContour, biggest, 2)
        pts1 = np.float32(biggest)
        pts2 = np.float32([[0, 0],[widthImg, 0], [0, heightImg],[widthImg, heightImg]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgWarped = cv2.warpPerspective(image, matrix, (widthImg, heightImg))
        cv2.imshow("warped", imgWarped)
        cv2.waitKey(0)
        return imgWarped
    else:
        print("contour not found")
        return None

def biggestContour(contours):
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 5000:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area
    return biggest,max_area

def reorder(myPoints): 
    myPoints = myPoints.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), dtype=np.int32)
    add = myPoints.sum(1)
 
    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] =myPoints[np.argmax(add)]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] =myPoints[np.argmin(diff)]
    myPointsNew[2] = myPoints[np.argmax(diff)]
 
    return myPointsNew

def drawRectangle(img,biggest,thickness):
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
 
    return img
