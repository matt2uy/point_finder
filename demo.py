# next: loop through a video?

# see how long it takes to process the image
import time
start_time = time.time()


###


import cv2
import numpy as np
 

# image/video files
image = "ball.jpg"

# save image as a "matrix"
matrix =  cv2.imread(image)
 
# get image properties
height, width, bpp = np.shape(matrix)
 
# traverse every pixel in the image. 
#(maybe iterate through every (12?) pixels to increase speed?)
num_of_pixels = 0
for pixel_y in range(0, height):
    for pixel_x in range(0, width):
        num_of_pixels += 1
        #print (matrix[pixel_y][pixel_x])

print ("there are", num_of_pixels, "pixels in this image")
print (matrix[200][100])









print("--- %s seconds ---" % (time.time() - start_time))