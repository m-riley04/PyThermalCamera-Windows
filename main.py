'''
Les Wright 21 June 2023
https://youtube.com/leslaboratory
A Python program to read, parse and display thermal data from the Topdon TC001 Thermal camera!

Forked by Riley Meyerkorth on 17 January 2025 to modernize and clean up the program for Windows and the TS001.
'''

import logging, cv2.utils.logging, os, sys
from datetime import datetime
from src.models.deviceinfo import DeviceInfo
from src.parsers.cli_parser import createParser
from src.defaults.values import DEFAULT_LOG_LEVEL, DEFAULT_VIDEO_DEVICE_INDEX
from src.defaults.devices import printAllSupportedDevices
from src.controllers.thermalcameracontroller import ThermalCameraController

# Determine base directory
if getattr(sys, 'frozen', False): base_dir = os.path.dirname(sys.executable)
else: base_dir = os.path.dirname(__file__)

# Initialize argument parsing
parser = createParser()
args = parser.parse_args()

# Initialize logging
logsDirPath = os.path.join(base_dir, "logs")
logFilePath = os.path.join(logsDirPath, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

if not os.path.exists(logsDirPath): os.makedirs(logsDirPath)

logging.basicConfig(filename=logFilePath, level=logging.INFO, format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("PyThermalCamera")
logger.info("Program started.")

def main():
    logger.info("Parsing command-line arguments.")
    subcommand = getattr(args, 'subcommand', None)
    device_info = None

    logger.info(f"Processing subcommand: {subcommand}")
    match subcommand:
        case "list":
            logger.info("Listing all supported devices from devices folder.")
            printAllSupportedDevices()
            return
        case "device":
            json_path = getattr(args, 'json_path', None)
            if json_path is None:
                logger.error("No JSON file path provided for device subcommand.")
                print("Error: A JSON file path is required when using the device subcommand.")
                return
            if not os.path.isfile(json_path):
                logger.error(f"Provided JSON file path does not exist: {json_path}")
                print(f"Error: The provided JSON file path does not exist: {json_path}")
                return
            if not json_path.endswith(".json"):
                logger.error(f"Provided file is not a JSON file: {json_path}")
                print(f"Error: The provided file is not a JSON file: {json_path}")
                return
            logger.info(f"Loading device information from JSON file: {json_path}")
            device_info = DeviceInfo.createFromJson(json_path)
        case _:
            parser.print_help()
            return

    # get global arguments/options
    logger.info("Retrieving global arguments.")
    device_index = getattr(args, 'device_index', DEFAULT_VIDEO_DEVICE_INDEX)
    debug = getattr(args, 'debug', False)
    verbose = getattr(args, 'verbose', False)
    quiet = getattr(args, 'quiet', False)
    logging_level = "DEBUG" if debug else str(getattr(args, 'log_level', DEFAULT_LOG_LEVEL)) # TODO: add default consts for these

    # Set logging config based on arguments
    # TODO: add logic for verbose and quiet (e.g. add console handler if verbose, set level to CRITICAL if quiet, etc.)
    logger.info(f"Setting logging level to {logging_level}.", )
    cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR) # TODO: add argument for specifically OpenCV. For now, I only want errors.
    logger.setLevel(logging_level)
        
    # Initialize the controller
    c = ThermalCameraController(
        device=device_info
        , device_index=device_index
        , logger=logger.getChild("ThermalCameraController")
    )
    
    # Print the all info needed on startup
    c.printCredits()
    c.printBindings()
    
    # Start the controller
    logger.info("Entering main runtime block.")
    try:
        c.run()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Exiting program.")
        print("Exiting program.")
    except Exception as e:
        logger.exception("An error occurred during the main runtime loop: ", exc_info=e)
        print(f"An error occurred: {e}")

    logger.info("Program ended.")
    
# Basic main call 
if __name__ == '__main__':
    main()