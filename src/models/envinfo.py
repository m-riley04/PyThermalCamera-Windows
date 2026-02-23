from dataclasses import dataclass

from defaults.values import DEFAULT_DEVICE_FPS, DEFAULT_DEVICE_NAME, DEFAULT_DEVICE_TEMP_MAX_C, DEFAULT_DEVICE_TEMP_MIN_C, DEFAULT_SENSOR_HEIGHT_PX, DEFAULT_SENSOR_WIDTH_PX, DEFAULT_VIDEO_DEVICE_INDEX
from helpers.env_checks import is_raspberrypi

@dataclass
class EnvInfo:
    """
    A dataclass to hold information about the environment the program is running in.
    This can be used to adjust behavior based on the environment, such as if we're running on a Raspberry Pi or not.
    """
    isPi: bool = is_raspberrypi()