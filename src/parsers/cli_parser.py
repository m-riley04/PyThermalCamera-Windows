

from argparse import ArgumentParser
from src.defaults.values import DEFAULT_VIDEO_DEVICE_INDEX

def addGlobalArgs(parser: ArgumentParser) -> None:
    """Adds the global options/args so they can be reused on main and subparsers."""
    parser.add_argument(
        "-i"
        , "--device-index"
        , dest="device_index"
        , type=int
        , default=DEFAULT_VIDEO_DEVICE_INDEX
        , help=f"VideoDevice index from OpenCV. Default is {DEFAULT_VIDEO_DEVICE_INDEX}.")
    
    parser.add_argument(
        "-d"
        , "--debug"
        , dest="debug"
        , action="store_true"
        , help="Enable debug logging. An alias to set the log level to DEBUG without having to use the --log-level argument. This also overrules --log-level if both are provided.")

    parser.add_argument(
        "--log-level"
        , dest="log_level"
        , choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        , default="WARNING"
        , help="Set the logging level. The lowest is DEBUG (log everything), and the highest is CRITICAL.")
    
    parser.add_argument(
        "-v"
        , "--verbose"
        , dest="verbose"
        , action="store_true"
        , help="Sends logs to the console in addition to the log file. This is useful for debugging, but can be overwhelming if there are a lot of logs.\nTODO: this needs to be implemented")
    
    parser.add_argument(
        "-q"
        , "--quiet"
        , "-s"
        , "--silent"
        , dest="quiet"
        , action="store_true"
        , help="Supresses all console output.\nTODO: this needs to be implemented")

def createParser() -> ArgumentParser:
    """
    Creates the main argument parser for the CLI.
    This is separated from main.py to avoid cluttering the main file with argument parsing code.
    """
    parser = ArgumentParser()

    # Add global arguments to the main parser so they can be used with any subcommand
    addGlobalArgs(parser)

    parserSubcommands = parser.add_subparsers(title="subcommands", dest="subcommand")

    # Device subcommand setup
    parserDevice = parserSubcommands.add_parser(
        "device"
        , help="Load device properties from a JSON file. Pass the path to a device JSON file (e.g. devices/TC001.json).")
    addGlobalArgs(parserDevice)
    parserDevice.add_argument(
        "json_path"
        , type=str
        , help="Path to a device JSON file to load. See the devices/ folder for examples.")

    parserList = parserSubcommands.add_parser(
        name="list"
        , help="Lists all available video devices and their indices."
        , description="Lists all available video devices and their indices. This can be used to determine the correct device index to use with the --device-index argument.")
    addGlobalArgs(parserList)

    return parser