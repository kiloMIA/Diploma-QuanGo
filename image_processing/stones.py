import cv2

def find_stones(board):
    img = board.copy()
    blur = cv2.medianBlur(img, 5)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)

    thresh_for_black_dots = cv2.threshold(gray,100,255, cv2.THRESH_BINARY_INV)[1]
    thresh_for_white_dots = cv2.threshold(gray,200,255, cv2.THRESH_BINARY)[1]

    cnts_for_black_dots = cv2.findContours(thresh_for_black_dots, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_for_white_dots = cv2.findContours(thresh_for_white_dots, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cnts_for_black_dots = cnts_for_black_dots[0] if len(cnts_for_black_dots) == 2 else cnts_for_black_dots[1]
    cnts_for_white_dots = cnts_for_white_dots[0] if len(cnts_for_white_dots) == 2 else cnts_for_white_dots[1]

    min_area = 1

    for c in cnts_for_white_dots:
       area = cv2.contourArea(c)
       if area > min_area:
          cv2.drawContours(img, [c], -1, (36, 255, 12), 2)
            
    for c in cnts_for_black_dots:
       area = cv2.contourArea(c)
       if area > min_area:
          cv2.drawContours(img, [c], -1, (36, 255, 12), 2)


    cv2.imshow('Output image:', img)
    cv2.waitKey()
