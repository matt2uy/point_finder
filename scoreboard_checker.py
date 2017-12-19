# small version of t-10, 8, 6, 4, 2...

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
- compare with equivalent pixels 5 seconds ago
- if different value: increment pixels_changed
- if pixels_changed is high enough: mark this as an event.
= 

Branch:
- sweep with 5+ points wihtin 4-7 seconds
- then only register score if 50%+ changed.

'''

### Variables
# how far (in frames) back we are comparing the current frame to.
sweep_length = 6
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
back_end_frame_values = [] # same as above ("sweep_length" frames behind)
pixels_changed = 0



# traverse through all pixels of current frame
for frame_index in range(num_of_frames):
	# if last frame, compare with 2 frames ago.
	if frame_index == num_of_frames-1: # temporary: check last frame only
		print("comparing with", sweep_length, "frames ago")
		# make a function for this? are rows/columns fixed? display resolution
		for row_index in range(height):
			# if a certain pixel location is a different value, increment pixels_changed
			for pixel_index in range(width):
				# turn this "inequality" into a delta or something later.
				if historical_frame_values[frame_index-sweep_length][row_index][pixel_index] != historical_frame_values[frame_index][row_index][pixel_index]:
					pixels_changed += 1

				back_end_frame_values.append(historical_frame_values[frame_index-sweep_length][row_index][pixel_index])
				current_frame_values.append(historical_frame_values[frame_index][row_index][pixel_index])

	print ("")


print (back_end_frame_values)
print("vs.")
print (current_frame_values)
print ("pixels_changed:", pixels_changed)