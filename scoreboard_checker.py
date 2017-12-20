# small version of t-10, 8, 6, 4, 2...
# more robust than simply looking at background subtraction.

# not using background subtraction
historical_frame_values = [
							[[0, 0, 0, 0, 0, 0], 
							[0, 1, 1, 1, 0, 0],
							[0, 1, 0, 0, 0, 0],
							[0, 1, 1, 1, 0, 0],
							[0, 0, 0, 0, 0, 0]],

						  	[[0, 0, 0, 0, 0, 0], 
							[0, 1, 1, 1, 0, 0],
							[0, 1, 0, 0, 0, 0],
							[0, 1, 1, 1, 0, 0],
							[0, 0, 0, 0, 0, 0]],

						  	[[0, 0, 0, 0, 0, 0], 
							[0, 1, 1, 1, 0, 0],
							[0, 1, 0, 0, 0, 0],
							[0, 1, 1, 1, 0, 0],
							[0, 0, 0, 0, 0, 0]],

						  	[[0, 0, 0, 0, 0, 0], 
							[0, 0, 0, 1, 0, 0],
							[0, 0, 0, 1, 0, 0],
							[0, 1, 1, 1, 0, 0],
							[0, 0, 0, 0, 0, 0]],

						  	[[0, 0, 0, 0, 0, 0], 
							[0, 0, 0, 1, 0, 0],
							[0, 0, 0, 1, 0, 0],
							[0, 1, 1, 1, 0, 0],
							[0, 0, 0, 0, 0, 0]],

						  	[[0, 0, 0, 0, 0, 0], 
							[0, 0, 0, 1, 0, 0],
							[0, 0, 0, 1, 0, 0],
							[0, 1, 1, 1, 0, 0],
							[0, 0, 0, 0, 0, 0]],

						  	[[0, 0, 0, 0, 0, 0], 
							[0, 0, 0, 1, 0, 0],
							[0, 0, 0, 1, 0, 0],
							[0, 1, 1, 1, 0, 0],
							[0, 0, 0, 0, 0, 0]],

						  ]

def find_scoreboard_change():
	...
''' Sweep with two points:
- 
- compare with equivalent pixels 6 seconds ago
- now compare with t-5, 4, 3, 2
- if the above increments were not enough, go into decimals.
- if pixels_changed is high enough: mark this as an event.
= 

Branch:
- sweep with 5+ points wihtin 4-7 seconds
- then only register score if 50%+ changed.

'''

# compares current frame with a past frame.
def find_pixels_changed(historical_frame_values, comparison_frame_distance):
	''' Find the number of pixels that have "changed" between 2 frames.
	Return the number of pixels that have a delta that surpass the given
	threshold.

	'''

	### Variables (should they be passed in as parameters?)
	# how far (in frames) back we are comparing the current frame to.
	#comparison_frame_distance = 6
	# pixel value differential (grayscale) required to register as a "changed pixel"
	pixel_value_threshold = 50
	# number of pixels needed to be changed for an event to be registered.
	pixels_changed_threshold = 2 


	# get height and width of display
	# double check this later...x/y-axis may be mixed up.
	width = len(historical_frame_values[0][0])
	height = len(historical_frame_values[0])
	num_of_frames = len(historical_frame_values)

	current_frame_values = [] # just a 1D list, with rows concatenated to one line.
	back_end_frame_values = [] # same as above ("comparison_frame_distance" frames behind)
	pixels_changed = 0

	# traverse through all pixels of current frame
	for frame_index in range(num_of_frames):
		# if last frame, compare with 2 frames ago.
		if frame_index == num_of_frames-1: # temporary: check last frame only
			#print("comparing current frame with t-" + str(comparison_frame_distance))
			# make a function for this? are rows/columns fixed? display resolution
			for row_index in range(height):
				# if a certain pixel location is a different value, increment pixels_changed
				for pixel_index in range(width):
					# turn this "inequality" into a delta or something later.
					if historical_frame_values[frame_index-comparison_frame_distance][row_index][pixel_index] != historical_frame_values[frame_index][row_index][pixel_index]:
						pixels_changed += 1

					back_end_frame_values.append(historical_frame_values[frame_index-comparison_frame_distance][row_index][pixel_index])
					current_frame_values.append(historical_frame_values[frame_index][row_index][pixel_index])

	'''
	print (back_end_frame_values)
	print("vs.")
	print (current_frame_values)
	'''
	return (pixels_changed)

# calls multiple historical frames
def get_historical_pixel_change(historical_frame_values):
	historical_pixel_changes = [] # in comparison to the current frame

	sweep_length = 6 # how far back (number of frames) we are going

	for comparison_frame in reversed(range(1, len(historical_frame_values))):
		historical_pixel_changes.append(find_pixels_changed(historical_frame_values, comparison_frame))

	print (historical_pixel_changes)	


get_historical_pixel_change(historical_frame_values)