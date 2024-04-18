import cv2
import numpy as np

def apply_watershed(ret, thresh, img):
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
     
# sure background area
    sure_bg = cv2.dilate(opening,kernel,iterations=3)
     
# Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
    ret, sure_fg = cv2.threshold(dist_transform, 0.7*dist_transform.max(),255,0)
     
# Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)

    ret, markers = cv2.connectedComponents(sure_fg)
    markers  = markers + 1
    markers[unknown==255] = 0.7
    markers = cv2.watershed(img, markers)
    img[markers == -1] = [0, 255, 0]
    cv2.imshow("stone", img)
    cv2.waitKey(0)
