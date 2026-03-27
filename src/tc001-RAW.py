import cv2
import numpy as np
import argparse

def getAllVideoDevices() -> list[int]:
	"""
	Returns a list of video device indexes for opencv. 
	Credit: Patrick Yeadon on StackOverflow - https://stackoverflow.com/questions/8044539/listing-available-devices-in-python-opencv
	"""
	index = 0
	arr = []
	while True:
		cap = cv2.VideoCapture(index)
		if not cap.read()[0]:
			break
		else:
			arr.append(index)
		cap.release()
		index += 1
	return arr

# Initialize argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--device", type=int, default=0, help=f"VideoDevice index from OpenCV")
args = parser.parse_args()
	
# Check if device specified
if args.device:
	dev = args.device
else:
	dev = 0

# Initialize video
cap = cv2.VideoCapture(dev)

# Initialize sensor properties (width, height, etc.)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cv2.namedWindow('Thermal',cv2.WINDOW_GUI_NORMAL)
font=cv2.FONT_HERSHEY_SIMPLEX

while(cap.isOpened()):
	# Capture frame-by-frame
	ret, frame = cap.read()

	if ret == True:
		cv2.namedWindow('Thermal',cv2.WINDOW_NORMAL)
		cv2.imshow('Thermal',frame)

		# Quit/exit signal
		keyPress = cv2.waitKey(3)
		if keyPress == ord('q'):
			break
			capture.release()
			cv2.destroyAllWindows()
