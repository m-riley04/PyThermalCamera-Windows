

from argparse import ArgumentParser

from src.defaults.values import DEFAULT_VIDEO_DEVICE_INDEX
from src.helpers.deviceHelper import getAllVideoDevices

def createParser() -> ArgumentParser:
    """
    Creates the main argument parser for the CLI.
    This is separated from main.py to avoid cluttering the main file with argument parsing code.
    """
    parser = ArgumentParser()

    # Device index argument is global, so we add it to the main parser instead of subparsers.
    parser.add_argument(
        "-i"
        , "--device-index"
        , dest="device_index"
        , type=int
        , default=DEFAULT_VIDEO_DEVICE_INDEX
        , help=f"VideoDevice index from OpenCV. Default is {DEFAULT_VIDEO_DEVICE_INDEX}.")

    parserSubcommands = parser.add_subparsers(title="subcommands", dest="subcommand")

    # Device subcommand setup
    parserDevice = parserSubcommands.add_parser(
        "device"
        , help="Load device properties from a JSON file. Pass the path to a device JSON file (e.g. devices/TC001.json).")
    parserDevice.add_argument(
        "json_path"
        , type=str
        , help="Path to a device JSON file to load. See the devices/ folder for examples.")

    parserList = parserSubcommands.add_parser(
        name="list"
        , help="Lists all available video devices and their indices."
        , description="Lists all available video devices and their indices. This can be used to determine the correct device index to use with the --device-index argument.")
    parserList.set_defaults(func=lambda args: print(getAllVideoDevices()))

    return parser