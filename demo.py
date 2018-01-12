'''
Matthew Uy 2017

Notes:

0. Look at t-10, 8, 6, 4, 2 frames to get scoreboard changes.

0.5. Look at the studies in the chrome tabs on the right.

1. why is it so slow? optimize (remove redundant stuff when traversing through each frame) 
	- maybe because I am "traversing" through every pixel in the frame.
	- isn't this advised against in the opencv documentation? because it's a "numpy array" or something?

2. clean up code -> remove cruft -> variable names -> refactor (modularize)

after: should we track colour change in rgb?
	- or (convert to greyscale first)?
	- or (convert to the opposite colour of the tennis court first)?

- - - - - - - - - - 

Resources:

- usask paper on tracking a tennis ball: http://www.collectionscanada.gc.ca/obj/s4/f2/dsk3/SSU/TC-SSU-08302006125935.pdf
- tennis ball + player tracking: http://epubs.surrey.ac.uk/733265/1/BMVC05.pdf

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

# Video files
video_path = "full_match.mp4" 

# opencv video attribute constants
VIDEO_CAPTURE_WIDTH = 3
VIDEO_CAPTURE_HEIGHT = 4
VIDEO_CAPTURE_FRAMES_PER_SECOND = 5

import cv2
import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip, concatenate_videoclips
import sys

##### Video Editing #####

def trim_video(start_time, end_time, new_file_path, source_file_path):
	''' Trim video using ffmpeg.
	note: not sure what unit 'start_frame' is. Is it frames/seconds/...etc?

	Sample, where video_path = "full_match.mp4":
	>>> trim_video(1000, 1100, "source_match.mp4", new_video_path)
	'''	
	video = VideoFileClip(source_file_path)

	# if the video ends before the point is finished:
	if end_time == -1:
		trimmed_video = video.subclip(start_time)
	else:
		trimmed_video = video.subclip(start_time, end_time)

	trimmed_video.write_videofile(new_file_path, codec='libx264') # codec is a default?
 
# note: is specifying the parameter type for only one function "inconsistent"?
# note: is there any video quality downgrade/lost artifacts? 

def merge_video(list_of_video_paths, new_file_path):

	list_of_videos = []
	for video_path in list_of_video_paths:
		list_of_videos.append(VideoFileClip(video_path))
	# note: why do the trimmed/merged clips freeze sometimes? is it ffmpeg?
	edited_video = concatenate_videoclips(list_of_videos)
	edited_video.write_videofile(new_file_path)

def cut_video_in_points_of_interest(point_timestamps):
	'''
	point_timestamps is in the form of: list[list[start_time, end_time]]
	'''
	list_of_video_paths = []

	for i in range(len(point_timestamps)):
		# video cuts before point ends
		if len(point_timestamps[i]) == 1: 
			trim_video(point_timestamps[i][0], -1, "auto_generated_files/newvid" + str(i) + ".mp4", video_path)
		# just a regular point
		else: 
			trim_video(point_timestamps[i][0], point_timestamps[i][1], "auto_generated_files/newvid" + str(i) + ".mp4", video_path)
		list_of_video_paths.append("auto_generated_files/newvid" + str(i) + ".mp4")
	# concatenate all trimmed video files.
	merge_video(list_of_video_paths, "edited_video.mp4")


'''# 8:50pm, 11/21/17
- remove later... once cut_video_in_points_of_interest is finished

- note that clean_up_noisy_timestamps() returns the provided parameter.
'''
'''
# the algorithm produces margins that are slightly off, so I manually added some for now
point_timestamps = [[13.0, 21.933333333333334-2], [37.4-1, 39.0+2], [56.833333333333336, 61.666666666666664], [82.4, 88.43333333333334], [95.3]]
# removed the floats -> kind of removed one pause for the last point
#point_timestamps = [[12-2, 22], [34-2, 39+2], [54-2, 62+2], [82-2, 88+2], [95]]

cut_video_in_points_of_interest(point_timestamps)
'''

##### Video Capture #####

def capture_video():
	# return historical_colour_value
	# Create a VideoCapture object and read from input file
	# If the input is the camera, pass 0 instead of the video file name
	cap = cv2.VideoCapture(video_path)
	fgbg = cv2.createBackgroundSubtractorMOG2()

	# Check if camera opened successfully
	if (cap.isOpened() == False): 
		print("Error opening video stream or file")

	historical_colour_value = []
	historical_pixel_values = []

	# note: fix the variable naming situation later
	# convert all of the 'box's and 'top'/'bottom' to a single scoreboard
	historical_top_box_colour_value = []
	previous_top_pixel_matrix = []
	historical_bottom_box_colour_value = []
	previous_bottom_pixel_matrix = []
	
	historical_scoreboard_matrix_values = [[], [], [], [], []]

	# get video properties
	width = int(cap.get(VIDEO_CAPTURE_WIDTH))
	height = int(cap.get(VIDEO_CAPTURE_HEIGHT))
	frames_per_second = float(cap.get(VIDEO_CAPTURE_FRAMES_PER_SECOND))
	num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # used for video length

	##### framing properties:
	### entire view
	left = 0#(width//10)
	right = width#width - (width//10)
	top = 0 #+ (height//3)
	bottom = height

	### scoreboard only
	scoreboard_left = 148
	scoreboard_right = 167
	# number on the first row of the scoreboard
	scoreboard_top_1 = 370
	scoreboard_bottom_1 = 390
	# number on the second row of the scoreboard
	scoreboard_top_2 = 398
	scoreboard_bottom_2 = 418
	scoreboard_epsilon = 5

	current_frame = 0

	# Read until video is completed
	while(cap.isOpened()):
		# Capture frame-by-frame
		ret, frame = cap.read()
		current_frame += 1
		
		#frame = cv2.blur(frame,(1,1))# gaussian blur

		if ret == True:
			############### Entire view
			total_colour_value = 0
			#################################### "Top half"
			'''left = (width//3)
			right = width - (width//3)
			top = 0# + (height//15)
			bottom = height//4
			cv2.rectangle(frame,(left, top),(right, bottom),(0,255,0),5) # test: draw it on top of the video
			

			# traverse every pixel in the image. 
			#(maybe iterate through every (12?) pixels to increase speed?) -> scale x,y?
			
			for pixel_y in range(top, bottom, 12):
				for pixel_x in range(left, right, 12):
					# save the 'total' average pixel value
					total_colour_value += frame[pixel_y][pixel_x][0] # indexes 0,1,2 = 'rgb'?
					total_colour_value += frame[pixel_y][pixel_x][1] 
					total_colour_value += frame[pixel_y][pixel_x][2]'''

			#################################### "Bottom half"
			'''left = 0#(width//10)
			right = width#width - (width//10)
			top = 0 + (height//3)
			bottom = height'''







			# 1. Look at the entire screen


			cv2.rectangle(frame,(left, top),(right, bottom),(0,255,0),5) # test: draw it on top of the video
			
			# traverse every pixel in the image. 
			#(maybe iterate through every (12?) pixels to increase speed?) -> scale x,y?
			#total_colour_value = 0

			for pixel_y in range(top, bottom, 12):
				for pixel_x in range(left, right, 12):
					# save the 'total' average pixel value
					total_colour_value += frame[pixel_y][pixel_x][0] # indexes 0,1,2 = 'rgb'?
					total_colour_value += frame[pixel_y][pixel_x][1] 
					total_colour_value += frame[pixel_y][pixel_x][2]

			#print(total_colour_value)
			historical_colour_value.append(total_colour_value)
			






			###############
			# 1. Look at the scoreboard (so we can see when the point ends)
			frame = fgbg.apply(frame) # background substraction seems to clean up the scorebaord area.


			changed_pixels = 0

			# 1.a) look at the the scoreboard

			# show where we are looking at:
			#cv2.rectangle(frame,(scoreboard_left, scoreboard_top_1),(scoreboard_right, scoreboard_bottom_1),(0,255,0),1)
			
			#print("Current time:", current_frame/frames_per_second)

			# traverse every pixel in the scoreboard.
			if len(historical_top_box_colour_value) > 0:
				current_pixel_index = 0
				for pixel_y in range(scoreboard_left, scoreboard_right, 1):
					for pixel_x in range(scoreboard_top_1, scoreboard_bottom_2, 1):
						
						# compare t-2, 4, 6, 8 and 10
						if frame[pixel_y][pixel_x] != previous_top_pixel_matrix[current_pixel_index]:#frame[pixel_y][pixel_x] > previous_top_pixel_matrix[current_pixel_index]+scoreboard_epsilon and frame[pixel_y][pixel_x] < previous_top_pixel_matrix[current_pixel_index]-scoreboard_epsilon:
							pixel_differential = frame[pixel_y][pixel_x]-previous_top_pixel_matrix[current_pixel_index]
							if pixel_differential > 100:
								changed_pixels += 1
						current_pixel_index += 1

						#changed_pixels += frame[pixel_y][pixel_x]#[0] # indexes 0,1,2 = 'rgb'?
						#changed_pixels += frame[pixel_y][pixel_x][1] 
						#changed_pixels += frame[pixel_y][pixel_x][2]
			
			previous_top_pixel_matrix = []
			## save previous pixel values from t-(2, 4, 6, 8, 10) seconds
			for pixel_y in range(scoreboard_left, scoreboard_right, 1):
				for pixel_x in range(scoreboard_top_1, scoreboard_bottom_2, 1):
					
					# compare stuff here?
					#frame_values.append(frame[pixel_y][pixel_x])

					previous_top_pixel_matrix.append(frame[pixel_y][pixel_x])


			# save pixel values at each second
			if current_frame % round(frames_per_second) == 0: # frames_per_second is somthing like 29.9699...
				'''for pixel_y in range(scoreboard_left, scoreboard_right, 1):
					for pixel_x in range(scoreboard_top_1, scoreboard_bottom_2, 1):
						previous_top_pixel_matrix.append(frame[pixel_y][pixel_x])'''
				historical_scoreboard_matrix_values[0].append(frame[pixel_y][pixel_x])
				# grab the values here, because this will occur once a second.
				#print(round(current_frame/frames_per_second, 2))

				# print percentage of video "traversed".
				i = int(round(current_frame/num_frames*100, 1))
				sys.stdout.write("\r%d%%" % i) # is there documentation for this? looks interesting.
				sys.stdout.flush()
				if i >= 99: # Add a newline when the progress text is complete.
					sys.stdout.write("\r%d%%" % 100)
					print ("")

			
			'''print (previous_top_pixel_matrix, "\n\n")
			#print (changed_pixels)
			if changed_pixels > 0:
				print("changed")
			else:
				print("not changed")'''
			

			# smooth out data:
			if changed_pixels > 10:
				changed_pixels = 10

			historical_top_box_colour_value.append(changed_pixels)


			###

			'''
			# 1.b) look at the "bottom" box
			changed_pixels = 0
			# show where we are looking at:
			#cv2.rectangle(frame,(scoreboard_left, scoreboard_top_1),(scoreboard_right, scoreboard_bottom_1),(0,255,0),1) # test: draw it on top of the video
			# traverse every pixel in the scoreboard.
			if len(historical_bottom_box_colour_value) > 0:
				current_pixel_index = 0
				for pixel_y in range(scoreboard_left, scoreboard_right, 1):
					for pixel_x in range(scoreboard_top_2, scoreboard_bottom_2, 1):
						if frame[pixel_y][pixel_x] != previous_bottom_pixel_matrix[current_pixel_index]:
							changed_pixels += 1
						current_pixel_index += 1

			previous_bottom_pixel_matrix = []
			# save previous pixel values
			for pixel_y in range(scoreboard_left, scoreboard_right, 1):
				for pixel_x in range(scoreboard_top_2, scoreboard_bottom_2, 1):
					previous_bottom_pixel_matrix.append(frame[pixel_y][pixel_x])

			# smooth out data:
			if changed_pixels > 10:
				changed_pixels = changed_pixels/5

			historical_bottom_box_colour_value.append(changed_pixels)
			'''
			




			################



			# Display the resulting frame
			#cv2.imshow('Frame', frame)

		 
			# Press Q on keyboard to exit
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
	 
		# Break the loop
		else: 
			break
	 
	# When everything is done, release the video capture object
	cap.release()
	 
	# Closes all the frames
	cv2.destroyAllWindows()

	return historical_colour_value, historical_top_box_colour_value

##### Video Data Processing #####

def get_modified_mean(list_of_values: int, mean_multiplier: float):
	''' Return the mean of the list_of_values, multiplied by the mean_multiplier.

	>>> get_modified_mean(displacement_list, 1.5)
	Returns the mean*1.5
	'''
	total_value = 0
	for value in list_of_values:
		total_value += value

	return (total_value/len(list_of_values))*mean_multiplier

def equalize_list_length(value, length):
	''' Duplicate the value until it is the same length as the
	raw list of values it is being compared to. For (visual) plotting
	purposes only.
	'''
	one_value_list = []
	for i in range(length):
		one_value_list.append(value)
	return one_value_list

def find_points_above_threshold(list_of_values, threshold, frames_per_second):
	''' Return a list of list of values, with elements of 
	index [x][1] being the "timestamp" ("x-axis", unit agnostic)
	and the index [x][0] being the "motion_value" ("y-axis")

	'''
	values_above_threshold = []

	for point_in_time in range(len(list_of_values)):
		if list_of_values[point_in_time] > threshold:
			values_above_threshold.append([point_in_time/frames_per_second, list_of_values[point_in_time]])

	return values_above_threshold

def find_points_within_threshold(list_of_values, upper_bound, lower_bound, frames_per_second):
	''' Return a list of list of values, with elements of 
	index [x][1] being the "timestamp" ("x-axis", unit agnostic)
	and the index [x][0] being the "motion_value" ("y-axis")

	'''
	values_within_threshold = []

	for point_in_time in range(len(list_of_values)):
		if list_of_values[point_in_time] < upper_bound and list_of_values[point_in_time] > lower_bound:
			values_within_threshold.append([point_in_time/frames_per_second, list_of_values[point_in_time]])

	return values_within_threshold

def get_derivative_of_list(list_of_values):
	''' Note: the list of derivatives will be one element lower than the input list.
	'''
	derivative_list = []
	#derivative_list.append(0)
	for i in range(len(list_of_values)):
		derivative_list.append(abs(list_of_values[i]-list_of_values[i-1]))
	# ensure that the list index 'lines up' with the chronological timeline
	derivative_list.pop(0)
	return derivative_list

def remove_singleton_frames(low_points):
	''' Remove 'points in time' that are 'singleton', or isolated 
	instances of low 'motion' value. 
	A 'singleton'/'isolated' value is defined as a value that does 
	not have any other value within 'delta' frames in each direction.
	Return the updated list.
	'''
	points_that_are_close = []
	previous_point = 0.0
	# 'closeness' of each frame (in secs). May be dependent on frames_per_second (1 sec/30 fps = 0.033).
	delta = (1/30) + 0.001 # added 0.001 because of? ... (maybe a rounding error? Dividing 1/30 over here does not result in repeating 3's?)
	
	for point_within_threshold in low_points:
		if point_within_threshold[0] < previous_point+delta and point_within_threshold[0] > previous_point-delta: 
			points_that_are_close.append([point_within_threshold[0], point_within_threshold[1]])
			#print (point_within_threshold[0], "is within", delta, "of", previous_point, len(points_that_are_close))
			

		previous_point = point_within_threshold[0]
	return points_that_are_close # reset -> maybe move the above code block into a function returning points_that_are_close

def get_serve_attempt_timestamps(low_points, high_points):
	''' Compare the high and low points, and maybe group them -> 
    -> thin the herd 
    -> get a distinct set of serve attempts (call the list 'point_start')

	'''
	high_low_delta = 1
	serve_attempts = []
	serve_attempt_delta = 5.0

	for low_point in low_points:
		for high_point in high_points:
			if low_point[0] < high_point[0] + high_low_delta and low_point[0] > high_point[0] - high_low_delta: 
		
				# narrow down serve_attempts
				serve_attempt_is_validated = True
				# if they are within serve_attempt_delta seconds of each other
				for serve_attempt in serve_attempts:
					if low_point[0] < serve_attempt + serve_attempt_delta and low_point[0] > serve_attempt - serve_attempt_delta:
						serve_attempt_is_validated = False
					

				if serve_attempt_is_validated:
					#print (low_point[0])
					serve_attempts.append(low_point[0])
	return serve_attempts

def convert_list_to_timestamps(list_of_values):
	# maybe use this if it takes too long to use 'every' frame. But it probably shouldn't take that long though.
	# scale the values to the appropriate time frame, given the fps of the video.
	# note: how do you get the fps of a video file? from ffmpeg? or OpenCV?
	# note: replace 30 with frames_per_second, once capture_video is refactored properly
	'''for i in range(0, len(raw), 1): 
		# maybe store in a dict instead.
		#frames_per_second = 
		#historical_colour_value[i/frames_per_second] = raw[i]
		historical_colour_value.append(raw[i])'''


	# get the first, second and third derivatives of the historical_colour_value list.
	displacement_list = get_derivative_of_list(list_of_values)
	velocity_list = get_derivative_of_list(displacement_list)
	acceleration_list = get_derivative_of_list(velocity_list)

	# Convert motion average data into a plotter-digestible format
	# displacement
	displacement_average = get_modified_mean(displacement_list, 1)
	displacement_average_list = equalize_list_length(displacement_average, len(displacement_list))

	# velocity
	velocity_average = get_modified_mean(velocity_list, 1)
	velocity_average_list = equalize_list_length(velocity_average, len(velocity_list))

	# acceleration
	acceleration_average = get_modified_mean(acceleration_list, 5)
	acceleration_average_list = equalize_list_length(acceleration_average, len(acceleration_list))

	acceleration_lower_average = get_modified_mean(acceleration_list, 1.5)
	acceleration_lower_threshold_list = equalize_list_length(acceleration_lower_average, len(acceleration_list))

	# note: replace 30 wtih frames_per_second
	high_points = find_points_above_threshold(acceleration_list, acceleration_average, 30)

	# delta is the range of y-values at which we are narrowing down our search.
	# Maybe make it represent an abs() value? ...
	# ... Currently it is not (see the function call below)
	threshold_delta = 100  
	low_points = find_points_within_threshold(acceleration_list, acceleration_lower_average, acceleration_lower_average-threshold_delta, 30)

	low_points = remove_singleton_frames(low_points)

	points_of_interest = get_serve_attempt_timestamps(low_points, high_points)

	# note: temp -> for testing
	#plot_graph([acceleration_list])

	return points_of_interest

def combine_timestamps_from_different_sources(timestamps_from_different_sources):
	all_points_of_interest = []
	for list_of_timestamps in timestamps_from_different_sources:
		for timestamp in list_of_timestamps:
			all_points_of_interest.append(timestamp)

	all_points_of_interest.sort() # using the built-in function
	return all_points_of_interest

def clean_up_noisy_timestamps(start_point_candidates, end_point_candidates): 
	''' Return a list of definitive start/end timestamps of each point.
	The list will be called point_timestamps. 
	It will be in the form of: list[list[start_time, end_time]]
	'''
	raw_timestamps = []
	point_timestamps = []

	# 1. put everything in a 2d list.
	# note: refactor this later. wrote this when groggy (11/21/17)
	for i in range(len(start_point_candidates)):
		raw_timestamps.append([start_point_candidates[i], 's'])
	for i in range(len(end_point_candidates)):
		raw_timestamps.append([end_point_candidates[i], 'e'])

	# sort all sublists in chronological order.
	unordered_timestamps = []
	for timestamp in raw_timestamps:
		# remove duplicates
		if timestamp[0] not in unordered_timestamps:
			unordered_timestamps.append(timestamp[0])

	for time in sorted(unordered_timestamps):
		if time in start_point_candidates:
			point_timestamps.append([time, 's'])
		else:
			point_timestamps.append([time, 'e'])

	'''Note (11/21/17): # do this later... 
	1. After the scoreboard end_point detection is fixed
	2. For now, work on the video editing section.
	'''
	# 2. Traverse the list and remove timestamps if they don't pass each filter.
	''' Filters:
	1. if point hasn't started and the timestamp is 'e', remove it.
	2. if point hasn't started and the timestamp is 's', start the point
	3. if the point has started and the timestamp is 'e' and the timestamp is at least 
	'''
	for i in range(len(point_timestamps)):
		point_in_progress = False

		if point_timestamps[i][1] == 'e' and not point_in_progress:
			point_timestamps[i][1] = 'n/a' # not possible

		elif point_timestamps[i][1] == 's' and not point_in_progress:
			point_in_progress = True

		elif point_timestamps[i][1] == 'e' and point_in_progress:
			point_in_progress = False




	# just a status update.. (to see what's going on before removing invalided timestamps)
	print ("- - - - - - - - - - - - - - - -")
	for point in point_timestamps:
		print (point)
	print ("- - - - - - - - - - - - - - - -")

	# remove invalidated timestamps
	fresh_timestamps = []
	for i in range(len(point_timestamps)):
		if point_timestamps[i][1] != 'n/a':
			fresh_timestamps.append(point_timestamps[i])
	point_timestamps = fresh_timestamps

	for point in point_timestamps:
		print (point)
	


	# 3. Reformat point_timestamps into the form ...
	#	 ... list[list[start_time, end_time]]

	# note: this is a temporary message, until scoreboard timestamping is fixed.
	return "hi"#point_timestamps 

'''# 8:50pm, 11/21/17 - remove later...
1. once timestamp detection is fixed
2. when clean_up_noisy_timestamps is finished after that.
print(clean_up_noisy_timestamps([13.0, 18.633333333333333, 37.4, 56.833333333333336, 82.4, 89.13333333333334, 95.3], \
	[0.03333333333333333, 0.03333333333333333, 5.033333333333333, 10.166666666666666, 16.933333333333334, 21.933333333333334, 39.0, 60.93333333333333, 61.666666666666664, 65.93333333333334, 88.43333333333334]))
'''

##### Diagnostic/Testing #####

def plot_graph(list_of_plots):
	""" Plot a graph using matplotlib, given a list_of_plots, which is a list
	of list of y values to be plotted. Each x-value in each list is separated 
	by a y-value of 1.	
	
	>>> plot_graph([acceleration_average_list, acceleration_list])
	# plots a graph of the acceleration values and their mean.
	"""

	for plot in list_of_plots:
		plt.plot(plot)
	plt.show() 


############################## 

if __name__ == '__main__':
	# Add test cases later?
	#import doctest
	#doctest.testmod()
	
	# maybe do a 'profile' to see how fast things are going?
	import time 
	start = time.time() # ^ like this?

	# Capture motion data from various "areas" of the video
	print("Capturing video...")
	historical_colour_value, scoreboard_first_row_values = capture_video()
	print("Done...")

	# print out time elapsed.
	end = time.time()
	elapsed = round(end - start, 2)
	print ("Video traversal took about", elapsed, "seconds.")
