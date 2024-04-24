import cv2
import numpy as np

import definitions

def apply_watershed(ret, thresh, img):
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
     
    # Sure background area
    sure_bg = cv2.dilate(opening,kernel,iterations=3)
    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
    ret, sure_fg = cv2.threshold(dist_transform, 0.4*dist_transform.max(),255,0)
     
    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)
    ret, markers = cv2.connectedComponents(sure_fg)
    markers  = markers + 1
    markers[unknown==255] = 0
    markers = cv2.watershed(img, markers)
    img[markers == -1] = [0, 255, 0]
    overlay_img = img.copy()

    unique_markers = np.unique(markers)
    for marker in unique_markers:
        if marker == -1 or marker == 0:
            continue  # Skip background and border markers
        
        marker_mask = np.zeros_like(markers, dtype=np.uint8)
        marker_mask[markers == marker] = 255
        
        contours, _ = cv2.findContours(marker_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in filter_contours(contours):
            cv2.drawContours(overlay_img, [contour], -1, (0, 255, 0), 2)  # Green contours
    
    cv2.imshow("Filtered Watershed on Original", overlay_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return overlay_img

def apply_clahe(img):
   lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
   l, a, b = cv2.split(lab)
   clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
   cl = clahe.apply(l)

   merged = cv2.merge((cl, a, b))
   eluminated = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
   return eluminated

def apply_split_channels(img, stone_color):
    b, g, r = cv2.split(img)
    if stone_color == "B":
        return r 
    else:
        return b

def apply_dilate(img):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3, 3))
    return cv2.dilate(img, kernel,
                              iterations=2,
                              borderType = cv2.BORDER_CONSTANT,
                              borderValue = definitions.COLOR_BLACK)

def apply_erode(img):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(100,100))
    kernel = cv2.resize(kernel, (3,3))
    return cv2.erode(img, kernel,
                          iterations=2,
                          borderType = cv2.BORDER_CONSTANT,
                          borderValue = definitions.COLOR_BLACK)

def filter_contours(contours):
    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 100 or area > 1000:
            continue
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * (area / (perimeter * perimeter)) if perimeter > 0 else 0
        if circularity > 0.7:
            filtered_contours.append(contour)
    return filtered_contours
