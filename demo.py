# next: refactor (make it neat asf in 30 mins)
# after: should we track colour change in rgb?
# or (convert to greyscale first)?
# or (convert to the opposite colour of the tennnis court first)?

'''
Resources:
- read/display/write to a video: https://www.learnopencv.com/read-write-and-display-a-video-using-opencv-cpp-python/
- loop through pixels: https://pythonspot.com/en/image-data-and-operations/
- sample gameplay image: https://i.ytimg.com/vi/nQ7fkaJJyF0/maxresdefault.jpg

- hough circle http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_houghcircles/py_houghcircles.html
- faster pixel loop? https://www.pyimagesearch.com/2017/08/28/fast-optimized-for-pixel-loops-with-opencv-and-python/

- more resources http://answers.opencv.org/question/69691/informative-websites-related-to-opencv/
- 'tennis' query: http://answers.opencv.org/questions/scope:all/sort:activity-desc/page:1/query:tennis/
- computer vision textbook: http://szeliski.org/Book/drafts/SzeliskiBook_20100903_draft.pdf

- edit a video with this? https://pypi.python.org/pypi/moviepy
... or this? https://gist.github.com/nkint/8576156
'''


# image/video files
image_path = "ball.jpg"
video_path = "test_match.mp4"

# see how long it takes to process the image
import time
start_time = time.time()


###

'''
import cv2
import numpy as np
 

# save image as a "matrix"
matrix =  cv2.imread(image_path)
 
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
'''



#play a video

import cv2
import numpy as np
 
# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture(video_path)
 
# Check if camera opened successfully
if (cap.isOpened()== False): 
	print("Error opening video stream or file")
 

num_of_frames = 0
 
# Read until video is completed
while(cap.isOpened()):
	# Capture frame-by-frame
	ret, frame = cap.read()
	if ret == True:
 
		num_of_frames += 1




		

		# image processing...

		# save image as a "matrix"
		#matrix =  cv2.imread(image_path)
		 
		# get image properties
		height, width, bpp = np.shape(frame)
		 
		# traverse every pixel in the image. 
		#(maybe iterate through every (12?) pixels to increase speed?) -> scale x,y?
		num_of_pixels = 0
		total_colour_value = 0
		for pixel_y in range(0, height, 12):
			for pixel_x in range(0, width, 12):
				num_of_pixels += 1
				# save the 'total' average pixel value
				total_colour_value += frame[pixel_y][pixel_x][0] # indexes 0,1,2 = 'rgb'?
				total_colour_value += frame[pixel_y][pixel_x][1] 
				total_colour_value += frame[pixel_y][pixel_x][2]

		
		#print ("there are", num_of_pixels, "pixels in this image")
		print ("total_colour_value:", total_colour_value)

		










		# Display the resulting frame
		cv2.imshow('Frame', frame)
	 
		# Press Q on keyboard to  exit
		if cv2.waitKey(25) & 0xFF == ord('q'):
			break
 
	# Break the loop
	else: 
		break
 
# When everything done, release the video capture object
cap.release()
 
# Closes all the frames
cv2.destroyAllWindows()






print("--- %s seconds ---" % (time.time() - start_time))
print ("num_of_frames:", num_of_frames)