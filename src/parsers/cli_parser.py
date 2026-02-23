

from argparse import ArgumentParser

from defaults.values import DEFAULT_DEVICE_FPS, DEFAULT_DEVICE_NAME, DEFAULT_DEVICE_TEMP_ACCURACY_C, DEFAULT_DEVICE_TEMP_MAX_C, DEFAULT_DEVICE_TEMP_MIN_C, DEFAULT_SENSOR_HEIGHT_PX, DEFAULT_SENSOR_WIDTH_PX, DEFAULT_VIDEO_DEVICE_INDEX
from enums.DeviceModelEnum import DeviceModel
from models.deviceinfo import DeviceInfo

def createParser() -> ArgumentParser:
    """
    Creates the main argument parser for the CLI.
    This is separated from main.py to avoid cluttering the main file with argument parsing code.
    """
    parser = ArgumentParser()

    # Device index argument is global since it applies to all models and manual mode, so we add it to the main parser instead of subparsers.
    parser.add_argument(
        "-i"
        , "--device-index"
        , dest="device_index"
        , type=int
        , default=DEFAULT_VIDEO_DEVICE_INDEX
        , help=f"VideoDevice index from OpenCV. Default is {DEFAULT_VIDEO_DEVICE_INDEX}.")

    parserSubcommands = parser.add_subparsers(title="subcommands")
        
    # Model subcommand setup
    parserModel = parserSubcommands.add_parser(
        "model"
        , help="Predefined models for the program. This can be used to quickly set all properties of a specific model without having to specify each property individually.")
    parserModel.add_argument(
        "model"
        , type=str
        , choices=[model.value for model in DeviceModel]
        , default=DeviceModel.TS001.value
        , help="Predefined models for the program. This can be used to quickly set all properties of a specific model without having to specify each property individually.")
    
    # Manual subcommand setup
    parserManual = parserSubcommands.add_parser(
        "manual"
        , help="Manually specify all properties of the device without using a predefined model. If no properties are specified, the default values will be used, which are based on the TS001.")

    ##=== Device properties arguments
    parserDeviceArgGroup = parserManual.add_argument_group("Device Properties")
    parserDeviceArgGroup.add_argument(
        "--temp-max"
        , dest="temp_max"
        , type=int
        , default=DEFAULT_DEVICE_TEMP_MAX_C
        , help=f"Maximum temperature readable by the device in Celsius. Default is {DEFAULT_DEVICE_TEMP_MAX_C}.")
    parserDeviceArgGroup.add_argument(
        "--temp-min"
        , dest="temp_min"
        , type=int
        , default=DEFAULT_DEVICE_TEMP_MIN_C
        , help=f"Minimum temperature readable by the device in Celsius. Default is {DEFAULT_DEVICE_TEMP_MIN_C}.")
    parserDeviceArgGroup.add_argument(
        "--temp-accuracy"
        , dest="temp_accuracy"
        , type=int
        , default=DEFAULT_DEVICE_TEMP_ACCURACY_C
        , help=f"Temperature accuracy of the device in Celsius. Default is {DEFAULT_DEVICE_TEMP_ACCURACY_C}.")
    parserDeviceArgGroup.add_argument(
        "--width"
        , dest="width"
        , type=int
        , default=DEFAULT_SENSOR_WIDTH_PX
        , help=f"Width of the sensor in pixels. Default is {DEFAULT_SENSOR_WIDTH_PX}.")
    parserDeviceArgGroup.add_argument(
        "--height"
        , dest="height"
        , type=int
        , default=DEFAULT_SENSOR_HEIGHT_PX
        , help=f"Height of the sensor in pixels. Default is {DEFAULT_SENSOR_HEIGHT_PX}.")
    parserDeviceArgGroup.add_argument(
        "-f"
        , "--frame-rate"
        , dest="frame_rate"
        , type=int
        , default=DEFAULT_DEVICE_FPS
        , help=f"Frame rate of the device. Default is {DEFAULT_DEVICE_FPS} FPS.")
    parserDeviceArgGroup.add_argument(
        "-n"
        , "--device-name"
        , dest="device_name"
        , type=str
        , default=DEFAULT_DEVICE_NAME
        , help=f"Name of the device. Default is {DEFAULT_DEVICE_NAME}.")

    return parser

def parseDeviceInfoFromArgs(args: object) -> DeviceInfo:
    """
    Parses the device information from the command line arguments and returns a DeviceInfo object with the parsed values.
    """
    name = getattr(args, 'device_name', DEFAULT_DEVICE_NAME)
    width = getattr(args, 'width', DEFAULT_SENSOR_WIDTH_PX)
    height = getattr(args, 'height', DEFAULT_SENSOR_HEIGHT_PX)
    temp_min = getattr(args, 'temp_min', DEFAULT_DEVICE_TEMP_MIN_C)
    temp_max = getattr(args, 'temp_max', DEFAULT_DEVICE_TEMP_MAX_C)
    temp_accuracy = getattr(args, 'temp_accuracy', DEFAULT_DEVICE_TEMP_ACCURACY_C)
    fps = getattr(args, 'frame_rate', DEFAULT_DEVICE_FPS)
    
    return DeviceInfo(
        name=name
        , width=width
        , height=height
        , temp_min_c=temp_min
        , temp_max_c=temp_max
        , temp_accuracy=temp_accuracy
        , fps=fps
    )