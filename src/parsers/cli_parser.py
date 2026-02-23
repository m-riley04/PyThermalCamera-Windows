

from defaults.values import DEFAULT_DEVICE_FPS, DEFAULT_DEVICE_NAME, DEFAULT_DEVICE_TEMP_MAX_C, DEFAULT_DEVICE_TEMP_MIN_C, DEFAULT_SENSOR_HEIGHT_PX, DEFAULT_SENSOR_WIDTH_PX, DEFAULT_VIDEO_DEVICE_INDEX
from models.deviceinfo import DeviceInfo


def parseDeviceInfoFromArgs(args: object) -> DeviceInfo:
    """
    Parses the device information from the command line arguments and returns a DeviceInfo object with the parsed values.
    """
    name = getattr(args, 'device_name', DEFAULT_DEVICE_NAME)
    index = getattr(args, 'device_index', DEFAULT_VIDEO_DEVICE_INDEX)
    width = getattr(args, 'width', DEFAULT_SENSOR_WIDTH_PX)
    height = getattr(args, 'height', DEFAULT_SENSOR_HEIGHT_PX)
    temp_min = getattr(args, 'temp_min', DEFAULT_DEVICE_TEMP_MIN_C)
    temp_max = getattr(args, 'temp_max', DEFAULT_DEVICE_TEMP_MAX_C)
    fps = getattr(args, 'frame_rate', DEFAULT_DEVICE_FPS)
    
    return DeviceInfo(name=name, index=index, width=width, height=height, temp_min_c=temp_min, temp_max_c=temp_max, fps=fps)