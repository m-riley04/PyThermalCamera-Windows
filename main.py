'''
Les Wright 21 June 2023
https://youtube.com/leslaboratory
A Python program to read, parse and display thermal data from the Topdon TC001 Thermal camera!

Forked by Riley Meyerkorth on 17 January 2025 to modernize and clean up the program for Windows and the TS001.
'''

import logging, cv2.utils.logging, os
from datetime import datetime
from src.models.deviceinfo import DeviceInfo
from src.parsers.cli_parser import createParser
from src.defaults.values import DEFAULT_LOG_LEVEL, DEFAULT_VIDEO_DEVICE_INDEX
from src.defaults.devices import printAllSupportedDevices
from src.controllers.thermalcameracontroller import ThermalCameraController

# Initialize argument parsing
parser = createParser()
args = parser.parse_args()

# Initialize logging
logsDirPath = "logs"
logFilePath = f"{logsDirPath}/log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

if not os.path.exists(logsDirPath):
    os.makedirs(logsDirPath)

logging.basicConfig(filename=logFilePath, level=logging.INFO, format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("PyThermalCamera")
logger.info("Program started.")

def main():
    subcommand = getattr(args, 'subcommand', None)
    if subcommand is None:
        parser.print_help()
        return

    device_info = None
    if subcommand == "list":
        logger.info("Listing all supported devices from devices folder.")
        printAllSupportedDevices()
        return
    
    if subcommand == "device":
        json_path = getattr(args, 'json_path', None)
        if json_path is None:
            logger.error("No JSON file path provided for device subcommand.")
            print("Error: A JSON file path is required when using the device subcommand.")
            return
        logger.info(f"Loading device information from JSON file: {json_path}")
        device_info = DeviceInfo.createFromJson(json_path)

    # get device index
    device_index = getattr(args, 'device_index', DEFAULT_VIDEO_DEVICE_INDEX)
    debug = getattr(args, 'debug', False)
    verbose = getattr(args, 'verbose', False)
    quiet = getattr(args, 'quiet', False)
    logging_level = "DEBUG" if debug else str(getattr(args, 'log_level', DEFAULT_LOG_LEVEL)) # TODO: add default consts for these

    # Set logging config based on arguments
    # TODO: add logic for verbose and quiet (e.g. add console handler if verbose, set level to CRITICAL if quiet, etc.)
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
    logger.info("Starting main runtime loop.")
    try:
        c.run()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Exiting program.")
        print("Exiting program.")
    except Exception as e:
        logger.exception("An error occurred during the main runtime loop.")
        print(f"An error occurred: {e}")

    logger.info("Program ended.")
    
# Basic main call 
if __name__ == '__main__':
    main()