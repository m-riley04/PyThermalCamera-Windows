import cv2

from defaults.devices import SUPPORTED_DEVICES
from enums.DeviceModelEnum import DeviceModel

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

def getSpecsByModel(model: DeviceModel) -> dict:
    """
	Get specifications for a device model.
	"""
    if model not in SUPPORTED_DEVICES:
        # Default to TC001 if unknown
        return SUPPORTED_DEVICES[DeviceModel.TC001]
    return SUPPORTED_DEVICES[model]