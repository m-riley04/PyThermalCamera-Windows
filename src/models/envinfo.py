from dataclasses import dataclass

from src.helpers.env_checks import is_raspberrypi

@dataclass
class EnvInfo:
    """
    A dataclass to hold information about the environment the program is running in.
    This can be used to adjust behavior based on the environment, such as if we're running on a Raspberry Pi or not.
    """
    isPi: bool = is_raspberrypi()