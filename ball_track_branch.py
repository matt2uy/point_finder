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
				print(round(current_frame/frames_per_second, 2))
				#print("a sec")

			
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

	# Capture motion data from various "areas" of the video
	print("Capturing video...")
	historical_colour_value, scoreboard_first_row_values = capture_video()
	print("Done...")

	### sample data (~100 seconds of a match)
	#historical_colour_value = [750459, 750587, 750930, 750447, 750659, 750754, 751064, 750984, 751504, 751553, 752597, 752364, 751943, 752022, 752049, 752159, 752809, 752489, 752878, 753060, 752612, 752831, 752417, 752929, 752539, 752692, 752068, 752581, 751766, 751992, 752443, 752516, 752807, 752092, 752476, 752869, 752045, 753399, 752388, 751795, 752492, 751040, 752282, 750619, 752027, 750999, 751153, 750499, 750520, 751257, 750893, 751867, 752961, 751572, 752053, 752872, 751084, 753145, 752492, 751685, 752891, 752098, 752726, 751373, 752159, 751637, 751421, 753515, 752279, 752394, 753054, 751697, 752310, 752068, 752102, 751010, 751308, 751010, 750312, 751035, 750194, 751277, 751329, 750813, 749972, 750773, 749473, 749151, 749269, 749992, 750569, 749590, 749816, 750384, 750316, 750190, 750816, 749987, 750065, 750875, 750243, 750592, 750442, 750271, 751072, 750541, 749898, 750576, 750390, 749453, 749296, 750297, 750200, 750203, 749641, 749296, 749441, 749254, 748800, 749097, 747554, 747338, 747796, 746848, 747954, 748559, 748319, 748559, 749068, 748513, 748091, 748604, 748386, 747907, 747867, 747354, 747461, 747392, 747229, 748056, 747628, 747860, 747769, 748111, 747983, 748021, 747916, 747853, 748038, 748286, 748052, 748356, 748036, 748168, 748300, 748150, 747832, 747176, 747458, 747251, 747842, 747459, 747920, 748048, 748147, 748258, 748233, 748097, 748176, 748106, 748169, 748384, 748300, 748264, 748057, 748230, 748630, 748673, 748790, 748716, 749995, 749636, 748932, 748923, 748679, 748771, 749046, 749486, 749184, 749209, 749540, 749321, 749146, 749829, 749019, 749442, 749641, 749546, 749802, 749941, 749878, 749442, 749428, 749187, 749292, 749205, 748863, 748887, 749181, 749109, 749106, 749644, 750062, 749858, 750046, 749657, 750364, 750401, 750719, 750861, 750977, 750280, 749778, 749483, 749553, 749569, 749824, 749766, 749486, 748590, 749493, 750771, 750992, 751273, 751319, 751697, 751430, 750947, 750591, 751282, 750320, 750362, 750591, 750963, 750755, 749771, 748531, 747839, 748193, 749287, 749754, 750004, 749995, 750200, 749828, 749163, 749345, 749064, 749088, 748861, 749164, 749383, 749473, 749512, 749584, 749821, 749442, 749230, 748998, 749019, 749082, 749368, 749283, 749356, 749744, 749552, 749942, 749204, 749554, 749709, 749883, 750187, 750121, 751146, 751321, 751196, 751413, 751835, 751656, 751789, 751915, 751841, 751450, 750918, 750321, 750893, 751337, 750617, 750475, 750852, 751149, 750450, 750682, 750422, 750116, 750141, 750526, 750737, 750306, 750241, 750230, 749913, 749418, 750186, 750526, 750838, 750183, 750242, 750061, 749867, 750123, 750051, 749917, 749868, 749744, 749908, 750203, 750073, 749881, 750012, 749976, 749665, 749808, 749998, 750132, 749720, 749756, 750079, 750134, 749923, 749795, 750296, 750410, 750319, 750273, 750801, 750706, 750673, 750719, 750889, 751054, 751029, 751051, 751099, 750738, 750299, 750908, 750717, 750276, 750099, 750767, 750815, 749999, 749595, 749706, 749973, 750374, 750148, 750029, 750556, 750334, 750366, 750598, 750513, 750465, 750122, 750247, 750601, 750923, 750635, 750652, 751007, 750933, 750568, 750271, 750411, 750584, 750142, 749895, 749760, 750509, 751064, 750969, 750157, 749973, 750039, 750095, 750185, 750635, 750948, 750786, 750406, 750048, 749798, 750411, 750467, 751284, 751213, 751163, 751130, 751806, 752237, 752347, 752628, 752103, 752797, 751222, 752544, 751396, 749769, 749652, 749284, 749493, 749562, 748201, 749052, 749269, 748310, 748637, 747949, 748335, 747405, 747726, 747689, 747253, 747571, 748516, 747578, 748984, 747705, 747202, 746398, 746039, 745947, 746181, 746485, 746983, 746787, 747426, 747434, 747833, 748405, 748308, 748236, 748466, 748292, 748762, 748448, 748294, 748409, 748407, 748354, 748443, 748232, 748192, 748022, 747871, 748175, 747967, 748117, 747976, 747458, 746961, 747293, 748049, 748755, 747530, 748513, 748568, 748136, 750696, 749654, 749424, 750501, 751212, 751569, 751021, 751088, 751012, 750684, 750605, 751331, 751994, 751722, 752049, 751941, 751237, 751610, 751985, 751169, 752508, 751712, 751222, 749695, 750421, 749643, 748907, 749454, 750337, 750606, 749991, 749221, 749643, 750774, 751171, 751744, 751420, 750627, 752099, 751130, 750159, 749847, 750984, 751237, 751798, 752141, 751621, 752088, 752564, 752441, 752109, 752434, 752799, 752608, 751965, 751884, 751868, 752179, 751788, 750558, 747864, 746846, 745813, 745843, 746121, 746313, 746941, 747113, 746974, 746620, 746907, 746936, 747040, 746411, 746604, 746447, 746229, 746330, 745610, 745473, 744892, 745299, 745273, 745415, 746373, 746215, 746688, 746865, 746653, 746370, 745876, 745779, 746675, 747477, 747705, 746946, 745923, 746369, 747200, 747295, 747177, 747769, 748399, 747932, 747503, 747780, 748051, 748430, 747647, 747459, 747415, 747734, 747533, 747462, 747451, 747636, 747883, 747598, 747623, 747538, 749829, 749872, 750094, 750212, 750297, 750526, 749906, 749460, 749214, 749548, 749338, 749060, 749050, 749233, 749392, 749756, 749996, 749798, 749537, 749627, 749883, 749914, 749927, 750025, 750458, 750658, 750979, 750961, 751475, 751294, 751536, 751567, 751481, 751008, 751181, 750876, 750446, 750353, 750482, 750307, 749944, 749875, 749877, 750192, 750218, 749668, 749969, 750136, 750383, 750614, 750445, 750035, 749551, 749634, 749885, 750103, 750126, 749741, 749473, 748679, 748286, 749237, 749419, 749777, 749687, 749337, 749355, 749637, 748946, 748501, 748463, 748315, 747983, 748290, 748992, 750306, 749816, 749870, 749992, 749475, 749407, 749200, 749035, 749395, 749229, 749580, 749189, 748194, 747724, 747309, 747821, 748014, 747661, 746929, 746793, 747055, 747573, 747617, 746970, 747368, 747807, 747999, 747899, 747539, 747341, 747700, 747282, 746963, 747491, 748085, 748795, 749434, 749171, 749024, 749025, 748989, 748661, 748427, 748471, 748471, 746874, 747455, 747705, 748057, 748022, 747304, 747280, 747352, 747643, 747828, 748065, 748547, 748770, 748559, 748703, 748539, 748349, 748638, 748307, 748334, 748473, 748499, 747779, 747418, 746983, 746975, 747131, 747004, 747017, 747049, 747064, 746755, 746975, 746925, 747083, 747137, 747276, 747132, 747217, 747116, 747009, 746987, 747195, 747291, 747425, 747533, 747554, 747350, 747163, 747003, 747056, 746880, 747047, 746991, 747210, 747201, 747422, 747523, 747586, 747562, 748290, 748437, 748557, 748609, 748897, 748954, 749027, 749055, 748843, 748729, 748399, 748058, 747892, 748065, 747989, 747926, 748030, 747899, 747761, 747632, 747804, 747852, 747978, 748096, 748254, 747972, 747951, 748293, 748905, 748881, 749089, 748594, 748607, 748036, 748226, 748376, 748523, 748502, 748796, 748721, 748805, 748941, 748844, 748724, 748648, 748780, 749074, 749666, 749714, 749873, 750171, 750405, 750130, 750617, 750776, 751439, 751518, 751192, 751329, 751439, 751304, 751346, 751371, 751607, 751048, 750770, 750913, 750245, 750008, 749835, 749599, 749686, 750054, 749726, 749195, 749142, 749338, 749226, 749097, 749128, 749253, 749640, 749476, 749589, 749073, 748852, 748917, 748854, 748837, 748888, 749005, 748961, 748966, 748900, 748700, 748628, 748634, 748641, 748651, 748877, 749007, 748922, 749048, 749154, 749351, 749347, 749429, 749514, 749504, 749509, 749422, 749392, 749167, 749214, 749286, 749121, 749357, 749607, 749357, 749419, 749256, 749109, 748980, 748621, 748411, 748512, 748605, 748805, 748887, 748782, 748710, 748858, 749254, 749217, 749304, 749701, 750446, 750125, 750808, 751210, 751424, 751306, 751200, 751522, 751798, 751871, 751935, 751839, 751948, 751459, 751074, 750899, 751020, 750703, 750443, 749972, 749662, 749437, 749166, 748891, 748857, 749137, 749108, 749048, 749155, 749343, 749745, 749862, 750211, 751028, 751479, 751756, 751877, 751918, 752426, 753183, 753253, 752783, 753458, 753631, 752774, 752506, 752896, 752215, 751976, 752029, 752183, 752528, 752974, 753428, 753266, 752749, 752470, 752261, 752073, 752036, 751711, 751828, 751640, 750980, 750680, 750753, 751425, 751612, 751685, 751781, 751780, 751734, 751698, 751553, 751491, 751502, 751050, 751652, 752136, 752239, 752512, 752451, 752313, 751913, 752128, 752169, 752348, 752184, 751980, 751786, 751782, 751918, 752451, 752707, 752930, 753029, 752768, 752091, 751993, 751884, 751819, 752210, 752074, 752071, 752417, 752668, 752764, 752728, 752671, 752576, 752532, 752315, 752127, 751885, 752385, 752983, 753281, 753798, 754331, 754053, 754410, 754579, 754570, 754533, 754312, 754300, 754291, 754123, 754110, 754045, 753644, 753458, 753204, 753007, 752880, 752869, 752598, 752570, 752601, 752566, 752822, 752967, 752965, 752834, 752583, 752467, 752199, 752830, 753014, 753330, 753329, 753179, 753391, 753435, 753430, 753321, 753631, 753759, 753833, 753221, 753468, 753512, 753578, 753464, 753575, 752658, 752799, 751658, 751054, 750819, 749719, 749472, 750335, 751129, 751570, 752030, 752177, 751831, 751869, 752702, 752460, 752232, 752644, 752071, 751277, 751899, 751368, 753411, 752811, 752355, 752277, 752077, 752652, 753636, 753236, 753182, 753409, 753790, 753250, 752939, 752162, 752279, 752021, 752267, 752005, 752279, 751859, 751944, 751809, 752178, 752575, 752759, 752731, 753102, 753384, 753342, 752124, 753731, 753251, 754481, 753164, 753961, 753008, 752560, 751403, 751717, 751676, 751727, 751375, 751621, 750896, 751201, 751268, 750322, 749899, 749485, 750572, 750172, 751108, 750943, 751991, 751710, 751007, 752169, 751649, 752458, 751716, 752464, 751596, 752521, 753062, 751307, 752217, 752172, 751738, 751532, 751963, 752504, 751809, 751695, 751422, 751488, 750714, 752550, 752292, 751751, 751570, 752475, 752152, 753545, 752240, 753185, 752682, 752509, 752058, 752425, 751060, 751911, 750753, 749994, 750262, 750684, 751317, 749874, 747240, 747477, 747924, 748099, 748315, 748872, 749808, 748384, 747456, 747765, 748038, 748080, 747724, 746864, 747020, 748527, 749037, 747653, 747455, 747800, 747470, 747871, 747379, 747643, 746677, 746799, 746047, 747508, 747295, 747044, 746588, 746902, 746832, 747193, 746239, 745760, 746769, 746482, 745774, 746785, 747221, 746393, 746237, 745542, 745072, 745021, 744497, 744812, 745950, 745702, 745948, 745110, 745165, 745288, 745668, 745873, 745771, 746202, 746200, 745536, 742558, 742785, 743524, 742688, 741585, 742469, 742336, 742050, 741537, 741940, 742594, 742058, 742271, 741047, 741392, 741273, 741150, 741451, 741056, 740891, 740663, 740609, 740839, 741408, 740830, 741150, 741162, 741147, 741251, 740831, 740881, 741563, 742199, 743436, 742798, 743289, 743395, 743288, 744094, 743464, 743400, 742740, 742590, 742529, 742918, 742725, 742283, 742665, 743065, 744376, 744954, 745305, 745104, 745167, 744387, 744678, 743646, 744865, 744604, 744000, 748401, 748355, 748905, 749655, 749645, 749219, 748269, 748396, 748761, 749141, 748328, 748652, 748688, 748545, 749161, 748489, 748960, 749189, 749244, 749631, 750096, 749625, 750083, 749912, 749509, 749980, 750204, 750816, 749667, 749822, 750029, 750059, 749290, 750017, 750457, 750305, 750156, 750668, 750376, 750280, 750131, 750123, 750388, 750444, 750339, 750680, 751507, 751146, 750767, 750990, 751182, 751101, 751310, 751155, 750716, 750533, 750330, 750461, 750521, 750322, 751204, 751496, 751683, 751804, 752196, 752163, 752260, 752139, 752174, 752103, 752006, 751963, 751641, 752043, 751990, 752165, 752075, 751830, 752204, 752028, 752020, 752174, 752087, 751718, 751854, 751684, 752465, 752605, 753070, 752764, 752523, 752387, 752444, 752268, 751966, 751824, 751703, 751582, 751520, 751860, 752329, 752808, 753122, 752996, 752883, 752676, 752597, 752563, 752508, 752283, 752212, 752270, 752340, 751811, 751839, 751626, 750889, 750854, 750724, 750243, 750084, 749892, 750140, 750739, 750698, 751027, 751676, 751586, 751310, 751375, 751141, 751030, 750699, 750824, 750298, 750776, 750883, 750396, 750504, 750234, 750414, 751007, 751512, 751567, 751413, 751347, 751398, 751216, 751126, 751207, 751337, 751390, 751351, 751099, 751055, 750770, 750863, 751343, 751014, 750963, 751054, 750936, 750760, 750270, 750117, 750704, 750846, 750201, 750110, 750069, 750075, 749824, 749858, 750060, 750397, 750573, 750180, 750108, 749693, 750179, 750767, 751315, 750796, 750732, 751070, 751334, 751264, 751012, 751324, 751214, 751002, 751022, 750857, 750715, 750597, 750926, 751157, 751629, 751699, 751997, 752005, 751845, 751729, 751476, 751351, 751509, 750910, 750753, 750098, 750561, 751215, 751265, 751362, 751199, 751339, 751328, 750911, 750602, 750640, 750369, 749775, 749859, 750007, 750092, 749611, 750443, 750101, 749463, 749847, 749824, 750023, 750106, 750258, 750510, 751013, 750992, 750580, 749867, 750094, 750525, 750858, 750380, 750307, 751016, 750528, 750228, 750064, 750240, 749912, 750328, 750285, 750654, 750799, 750318, 750032, 750360, 750423, 750691, 750363, 749781, 750290, 750497, 751533, 751175, 749854, 749894, 750358, 750654, 750989, 751007, 750851, 750989, 750999, 751356, 751067, 751545, 752056, 751852, 751722, 752246, 752219, 752006, 752428, 752009, 751213, 751426, 751888, 751744, 750974, 751345, 751322, 752138, 752098, 752613, 752139, 752634, 752358, 752075, 752653, 753312, 753132, 752931, 752945, 752920, 753082, 753534, 752404, 751813, 751931, 752416, 752369, 752160, 752637, 752879, 752945, 753035, 753321, 752650, 752497, 753664, 753610, 753343, 752672, 752912, 753089, 753532, 753786, 753982, 754078, 753776, 753665, 753549, 753755, 753973, 754037, 753968, 753558, 753281, 753511, 753164, 753219, 753449, 753559, 753613, 753763, 754066, 754339, 754257, 754065, 753909, 754000, 754057, 753924, 753798, 753459, 753135, 753844, 754068, 753268, 753730, 753764, 753515, 753156, 753151, 753011, 752908, 752733, 752593, 752574, 752499, 752940, 753473, 753912, 754002, 753248, 752947, 753180, 752531, 752746, 753030, 753095, 753127, 753034, 752884, 752545, 752319, 752387, 752880, 753215, 753127, 753281, 753209, 753053, 752894, 752730, 752944, 752843, 752821, 752645, 752183, 752560, 752578, 752427, 752156, 752185, 752053, 750614, 751339, 751901, 751717, 750614, 752141, 752529, 753003, 753230, 753160, 753190, 753030, 753020, 753257, 755588, 754761, 754716, 754859, 754596, 754692, 753857, 753894, 753902, 753388, 752873, 752552, 752639, 751807, 752522, 752768, 753432, 752738, 753194, 754019, 754074, 753850, 753650, 752992, 753206, 752192, 751808, 751513, 751001, 751706, 751463, 751610, 752102, 752190, 751903, 751815, 751769, 752083, 752422, 752770, 752931, 752778, 752756, 752934, 752901, 752750, 752720, 752740, 752761, 752454, 752174, 751407, 750961, 750940, 751673, 752358, 752276, 752210, 752229, 752115, 752113, 752427, 752782, 752785, 752447, 752219, 752184, 752345, 752148, 751864, 751793, 751239, 751019, 751134, 750660, 750626, 750065, 749453, 749776, 749707, 749969, 749918, 748927, 749484, 749432, 749277, 748623, 748630, 749072, 748239, 749175, 749604, 750182, 750077, 749785, 750032, 749016, 750593, 751188, 751985, 750147, 750573, 751826, 751750, 752175, 751760, 751268, 751487, 751871, 751645, 753145, 752645, 751298, 751199, 750211, 750998, 752033, 751028, 753708, 752556, 751919, 753653, 751702, 753668, 752288, 753370, 752583, 752964, 755097, 754273, 754041, 755585, 754720, 753145, 754147, 752987, 753953, 755144, 753896, 753053, 752775, 751452, 750570, 750921, 751199, 752253, 753088, 752915, 752732, 753603, 753327, 752193, 752891, 752191, 753170, 752978, 754604, 755048, 754652, 752949, 751361, 752732, 753014, 751512, 751624, 752309, 752560, 752758, 752311, 751434, 750177, 750493, 750935, 750096, 751197, 752411, 753208, 752684, 754852, 754103, 755764, 755018, 754803, 753937, 753134, 753933, 753765, 754155, 754238, 754675, 753759, 754051, 753019, 753240, 753798, 753425, 753677, 755362, 754415, 754652, 755048, 754203, 752281, 751984, 751808, 751548, 752459, 752967, 753637, 753213, 753528, 753303, 753047, 752383, 752393, 752249, 751645, 750092, 751347, 750445, 750637, 750067, 749762, 748786, 748340, 747992, 748251, 748586, 749756, 748698, 748278, 747423, 747208, 746757, 747044, 747139, 747713, 747790, 748008, 748096, 748324, 748913, 749618, 749439, 748453, 748626, 749034, 748527, 748628, 748817, 748597, 748237, 748130, 748120, 748296, 748428, 748715, 748666, 748787, 748853, 749220, 749454, 749371, 749187, 748842, 748708, 748641, 748509, 748918, 749156, 749829, 749866, 750185, 750276, 750222, 749808, 749554, 749571, 749740, 749391, 749802, 749799, 749769, 749553, 749575, 748866, 749006, 749239, 748861, 749276, 749225, 749281, 748390, 748397, 748038, 747670, 748136, 748642, 748695, 748770, 748292, 748707, 748686, 748868, 749030, 749071, 749488, 749504, 749777, 749946, 750121, 749653, 749670, 749869, 749670, 749288, 749346, 749479, 749838, 749849, 750075, 750046, 750328, 750074, 750046, 749737, 749544, 749864, 749941, 749934, 749815, 749742, 749605, 749762, 749669, 749558, 749218, 749174, 749228, 749150, 749150, 749575, 749428, 749160, 749090, 749294, 749202, 748743, 748300, 748231, 748020, 748192, 748768, 748852, 748607, 748930, 748880, 748708, 748807, 748956, 748391, 748563, 748219, 747971, 748049, 747900, 748063, 748022, 747815, 747769, 747613, 747691, 747263, 747064, 746970, 746709, 746458, 746653, 747072, 747429, 747717, 747904, 747983, 748196, 748178, 748465, 748392, 748289, 748323, 748143, 747789, 747480, 747364, 746913, 746852, 746684, 746561, 746771, 746851, 746955, 747076, 747259, 747575, 747655, 747845, 747942, 748092, 747951, 747825, 747561, 747544, 747702, 748498, 748661, 748674, 748779, 748350, 748207, 748046, 748022, 748232, 748507, 748472, 748273, 748350, 748199, 748502, 748663, 748755, 748506, 748247, 748355, 748182, 748172, 748634, 749113, 749529, 749523, 749491, 749759, 749784, 749706, 749621, 749650, 749590, 749541, 748922, 748881, 748715, 748567, 748237, 748368, 748293, 748393, 748595, 748489, 748528, 748917, 748790, 748834, 748833, 748982, 749061, 748987, 748734, 748518, 748412, 748464, 748621, 748377, 748404, 748583, 748662, 748890, 748955, 749126, 749194, 749443, 750453, 750548, 750887, 750943, 750662, 751046, 750926, 751252, 751542, 750726, 751359, 751716, 752482, 752413, 752672, 753127, 752785, 753076, 752268, 752431, 753195, 753163, 752890, 751614, 752765, 753274, 753614, 753491, 752350, 752726, 753764, 753086, 751915, 752545, 752988, 753482, 754349, 753910, 753731, 754039, 754338, 755173, 754282, 753650, 753551, 754087, 755351, 753875, 754116, 753953, 754215, 754098, 754840, 754458, 754810, 756146, 755074, 753673, 753307, 753782, 753632, 753923, 751989, 752223, 751955, 751535, 751749, 752838, 752143, 752427, 751656, 749867, 749086, 749670, 750503, 750751, 750522, 749935, 749041, 749607, 748508, 749555, 750146, 749623, 749894, 750118, 749403, 748418, 748139, 748121, 747781, 747555, 748338, 748118, 748606, 749607, 749528, 747930, 748820, 748970, 748170, 747238, 747353, 746947, 747378, 747089, 746862, 746771, 746995, 746397, 746204, 747373, 747844, 746205, 745883, 747181, 747015, 746165, 746340, 746110, 746139, 745797, 745479, 745086, 745561, 745704, 745749, 745781, 745216, 745113, 744756, 745297, 745480, 745034, 745027, 745123, 745742, 745371, 745038, 745017, 744947, 745319, 745283, 745198, 744966, 745150, 745316, 745110, 745328, 745245, 745219, 745644, 746520, 746219, 745959, 745946, 745829, 745757, 745804, 745908, 746047, 746330, 746572, 746549, 746630, 746736, 746968, 747167, 747132, 747530, 747944, 748362, 748161, 747879, 748102, 747786, 747524, 747733, 747834, 747494, 747320, 747743, 748204, 748270, 748175, 748272, 748456, 748181, 747851, 748165, 748081, 747893, 748018, 748029, 747616, 747706, 747816, 747734, 747703, 746962, 746796, 746594, 746576, 747174, 747008, 746985, 746836, 746648, 746658, 746295, 746709, 746292, 746034, 746249, 746279, 746626, 746998, 747051, 746927, 747071, 747370, 747749, 748095, 747816, 747720, 747209, 747479, 748140, 747999, 747142, 748001, 748633, 749087, 748543, 748688, 748496, 748198, 748145, 748603, 748248, 747792, 748093, 746713, 746461, 746383, 746677, 746532, 746760, 746888, 746634, 746645, 746590, 746599, 746628, 747289, 747464, 747736, 746931, 746330, 746292, 746130, 746142, 746079, 746656, 746954, 747453, 747822, 748126, 747896, 747541, 745921, 746116, 745848, 745334, 745648, 745561, 745265, 744820, 745282, 745080, 744994, 744334, 744399, 744882, 745376, 745925, 746438, 746099, 746412, 746074, 746697, 746046, 745792, 745502, 745009, 745225, 745626, 745471, 745596, 745811, 745334, 744190, 744697, 745594, 745333, 745221, 745222, 745078, 744116, 744211, 745475, 745217, 746708, 747364, 747359, 747826, 746694, 747287, 747324, 746497, 746732, 746190, 746046, 746091, 745901, 745934, 746149, 747009, 745417, 745626, 745684, 745903, 747112, 746310, 745535, 745202, 744697, 745926, 745343, 744264, 744336, 744851, 744743, 746136, 745122, 745793, 744760, 744257, 745135, 746479, 745433, 744298, 744176, 745472, 745366, 744210, 744590, 745789, 746235, 744040, 743363, 743352, 743917, 744363, 744714, 745238, 744347, 743702, 743924, 743523, 742634, 742297, 744694, 745067, 743896, 742841, 743224, 742779, 743314, 743085, 743631, 743974, 745045, 744923, 745492, 745837, 745883, 746480, 744538, 745423, 744882, 744790, 744397, 743971, 743645, 746014, 745068, 745379, 746496, 746419, 745793, 746242, 746007, 746559, 746944, 746338, 745870, 745141, 746592, 744981, 746337, 746779, 746504, 745809, 744580, 744814, 745714, 746061, 746481, 743574, 744160, 746378, 745570, 745899, 745247, 747039, 748478, 747361, 746161, 745674, 746575, 746587, 745255, 745117, 746533, 746240, 745377, 745681, 746699, 748054, 747282, 746653, 746728, 746820, 745871, 746515, 745815, 745872, 745972, 745540, 745642, 746895, 748481, 747100, 746580, 749045, 748920, 747624, 747196, 746217, 746874, 748291, 748855, 746977, 747581, 748066, 749656, 749454, 748547, 747628, 747315, 746765, 746573, 746756, 745790, 745398, 745110, 746286, 746741, 746772, 746726, 747221, 745653, 746517, 745830, 744100, 744672, 743603, 743720, 745178, 745540, 744856, 744156, 743144, 743665, 744016, 745034, 744459, 743964, 743144, 743977, 743935, 743647, 743834, 743821, 744669, 744176, 743509, 743800, 744793, 745740, 745625, 745329, 746527, 746042, 745877, 745650, 746221, 746135, 745864, 744937, 745079, 745830, 745370, 745893, 745386, 744740, 744199, 743634, 744416, 745794, 745583, 746072, 746014, 746116, 746352, 745624, 744919, 744432, 744668, 744162, 744272, 742247, 741780, 741098, 742486, 742653, 743069, 742896, 742446, 742888, 743265, 743760, 743620, 743744, 743746, 743875, 743828, 743414, 743250, 743003, 743508, 743206, 743182, 743093, 743173, 742891, 742924, 743418, 743037, 742916, 742991, 742789, 742723, 742475, 742290, 742380, 742092, 741884, 741661, 741465, 741815, 741609, 741407, 741618, 741514, 741611, 741825, 741855, 741914, 741567, 741667, 741645, 741422, 741345, 741248, 741639, 741725, 741800, 742010, 741755, 741547, 741776, 742020, 742315, 742066, 741908, 741837, 741644, 741417, 741384, 741273, 741159, 741191, 741442, 741756, 741994, 742233, 742564, 742678, 742676, 742592, 742752, 742815, 742646, 742503, 742513, 742709, 743138, 743189, 743401, 743860, 743759, 745003, 744478, 743640, 743825, 743947, 744135, 744507, 744468, 744582, 744555, 744990, 744699, 744568, 744586, 744756, 744559, 744727, 744752, 744656, 744716, 744593, 744682, 744437, 744384, 744336, 744278, 744455, 744410, 744341, 745615, 745243, 745217, 745030, 745009, 745402, 745464, 745009, 744680, 744495, 744460, 744679, 744580, 744308, 744472, 744707, 744655, 745150, 745534, 745317, 744869, 744740, 744303, 744042, 743846, 743581, 743206, 742854, 742851, 743097, 743137, 743097, 743265, 743150, 743305, 743435, 743324, 742922, 742934, 743284, 743270, 743302, 743505, 743961, 743993, 743699, 743886, 744482, 744385, 744103, 743825, 744259, 743543, 742914, 742831, 744110, 743956, 742786, 742060, 742347, 742920, 742727, 743483, 744629, 743875, 743954, 743770, 745402, 746227, 745669, 744444, 744175, 745292, 745176, 745800, 744630, 744112, 743723, 745503, 745431, 744729, 745441, 745763, 745138, 745481, 745321, 745347, 745396, 744816, 744511, 745382, 745528, 744281, 744772, 743976, 743313, 742801, 743030, 743655, 742778, 743358, 742853, 744442, 744409, 743370, 742445, 743583, 742580, 743077, 743175, 742603]
	#scoreboard_first_row_values = [48260, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2930, 2930, 2930, 2930, 2930, 2930, 2930, 2930, 2930, 2930, 2803, 2803, 2803, 2803, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 382, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 0, 0, 0, 0, 0, 0, 381, 382, 382, 127, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 127, 127, 0, 0, 0, 0, 0, 127, 127, 127, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 127, 127, 127, 127, 127, 127, 127, 127, 127, 127, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 127, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 381, 381, 381, 381, 381, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 127, 127, 127, 127, 127, 127, 127, 635, 635, 635, 635, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 508, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1016, 1016, 1016, 1016, 1016, 1016, 1016, 1016, 1016, 1016, 889, 889, 889, 889, 889, 889, 889, 5602, 21797, 44228, 65279, 81972, 86823, 84014, 72159, 57754, 39519, 24597, 13886, 8917, 8279, 9042, 7511, 5984, 5984, 5350, 5350, 5350, 5350, 5350, 5350, 5350, 5350, 5350, 5350, 5350, 5350, 5350, 5350, 4458, 4458, 4458, 4458, 4331, 4331, 4331, 4331, 4331, 4331, 4331, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 381, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 1275, 1275, 1275, 1275, 1275, 1275, 1275, 1275, 1275, 1275, 1020, 1020, 1020, 1020, 1020, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	#scoreboard_second_row_values = [48260, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2420, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6374, 16320, 26262, 37226, 53797, 76115, 86700, 96900, 95880, 92310, 86826, 81725, 74074, 64642, 62730, 56991, 56224, 53550, 44624, 23332, 8415, 1020, 1020, 1020, 1020, 1020, 1020, 3060, 3060, 3060, 3060, 3060, 3060, 3060, 3060, 3060, 3060, 3060, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

	''' 9:52 12/12/17
	plot_graph([scoreboard_first_row_values])

	start_point_candidates = convert_list_to_timestamps(historical_colour_value)#scoreboard_values)

	end_point_candidates = convert_list_to_timestamps(scoreboard_first_row_values)
	'''

	'''
	end_point_candidates = combine_timestamps_from_different_sources(\
		[convert_list_to_timestamps(scoreboard_first_row_values), \
		convert_list_to_timestamps(scoreboard_second_row_values)])'''

	''' 9:52 12/12/17
	print ("This is what will be edited:")
	print (clean_up_noisy_timestamps(start_point_candidates, end_point_candidates))
	'''
