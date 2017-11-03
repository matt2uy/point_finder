# import image and convert it to greyscale
'''
import cv2

image = cv2.imread("clouds.jpg")
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imshow("Over the Clouds", image)
cv2.imshow("Over the Clouds - gray", gray_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''

# play video from a file
import numpy as np
import cv2

cap = cv2.VideoCapture('test_match.mp4')

while(cap.isOpened()):
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow('frame',gray)
    if cv2.waitKey(25) & 0xFF == ord('q'): # modify the parameter x in cv2.waitkey(x) to modify (playback speed?)
        break

cap.release()
cv2.destroyAllWindows()