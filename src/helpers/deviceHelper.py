import cv2

from defaults.devices import SUPPORTED_DEVICES
from enums.DeviceModelEnum import DeviceModel
from models.deviceinfo import DeviceInfo

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

def printAllVideoDevices():
	"""
	Prints all available video devices and their indices to the console.
	"""
	devices = getAllVideoDevices()
	if not devices:
		print("No video devices found.")
	else:
		print("Available video devices:")
		for index in devices:
			print(f"Device Index: {index}")

def getInfoByModel(model: DeviceModel) -> DeviceInfo:
    """
	Get specifications for a device model.
	"""
    if model not in SUPPORTED_DEVICES:
        # Default to TC001 if unknown
        return SUPPORTED_DEVICES[DeviceModel.TC001]
    return SUPPORTED_DEVICES[model]

def getModelByName(name: str) -> DeviceModel | None:
	"""
	Get the DeviceModel enum member corresponding to a given device name string. 
	Returns None if no matching model is found.
	"""
	for model, info in SUPPORTED_DEVICES.items():
		if info.name.lower() == name.lower():
			return model
	return None