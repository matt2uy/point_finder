# next: loop through a video?
# after: should we track colour change in rgb?
# or (convert to greyscale first)?
# or (convert to the opposite colour of the tennnis court first)?

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
#(maybe iterate through every (12?) pixels to increase speed?) -> scale x,y?
num_of_pixels = 0
total_colour_value = 0
for pixel_y in range(0, height, 12):
    for pixel_x in range(0, width, 12):
        num_of_pixels += 1
        # save the 'total' average pixel value
        total_colour_value += matrix[pixel_y][pixel_x][0] # indexes 0,1,2 = 'rgb'?
        total_colour_value += matrix[pixel_y][pixel_x][1] 
        total_colour_value += matrix[pixel_y][pixel_x][2]

print ("there are", num_of_pixels, "pixels in this image")
print ("total_colour_value:", total_colour_value)

# div by 12 because we only check every 12th pixel
# and div by 3 because there are 3 values for rgb
average_pixel_value = total_colour_value / ((height/12)*(width/12)) / 3
print ("average_pixel_value:", average_pixel_value)









print("--- %s seconds ---" % (time.time() - start_time))