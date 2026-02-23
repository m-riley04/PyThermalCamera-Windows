from dataclasses import dataclass

from defaults.values import DEFAULT_DEVICE_FPS, DEFAULT_DEVICE_NAME, DEFAULT_DEVICE_TEMP_MAX_C, DEFAULT_DEVICE_TEMP_MIN_C, DEFAULT_SENSOR_HEIGHT_PX, DEFAULT_SENSOR_WIDTH_PX, DEFAULT_VIDEO_DEVICE_INDEX

@dataclass
class DeviceInfo:
    """
    Holds information about the thermal camera device, such as its index, resolution, and temperature range.
    The default values are for the Topdon TC001, but they can be overridden by command line arguments when running the program.
    """
    name: str = DEFAULT_DEVICE_NAME
    index: int = DEFAULT_VIDEO_DEVICE_INDEX
    width: int = DEFAULT_SENSOR_WIDTH_PX
    height: int = DEFAULT_SENSOR_HEIGHT_PX
    temp_min_c: int = DEFAULT_DEVICE_TEMP_MIN_C
    temp_max_c: int = DEFAULT_DEVICE_TEMP_MAX_C
    fps: int = DEFAULT_DEVICE_FPS