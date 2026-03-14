'''
Les Wright 21 June 2023
https://youtube.com/leslaboratory
A Python program to read, parse and display thermal data from the Topdon TC001 Thermal camera!

Forked by Riley Meyerkorth on 17 January 2025 to modernize and clean up the program for Windows and the TS001.
'''

from src.parsers.cli_parser import createParser
from src.defaults.values import DEFAULT_VIDEO_DEVICE_INDEX
from src.defaults.devices import loadDeviceFromJson, printAllSupportedDevices
from src.controllers.thermalcameracontroller import ThermalCameraController

# Initialize argument parsing
parser = createParser()
args = parser.parse_args()

def main():
    subcommand = getattr(args, 'subcommand', None)
    if subcommand is None:
        parser.print_help()
        return

    device_info = None
    if subcommand == "list":
        printAllSupportedDevices()
        return
    
    if subcommand == "device":
        json_path = getattr(args, 'json_path', None)
        if json_path is None:
            print("Error: A JSON file path is required when using the device subcommand.")
            return
        device_info = loadDeviceFromJson(json_path)

    # get device index
    device_index = getattr(args, 'device_index', DEFAULT_VIDEO_DEVICE_INDEX)
        
    # Initialize the controller
    c = ThermalCameraController(
        device=device_info
        , device_index=device_index
    )
    
    # Print the all info needed on startup
    c.printInfo()
    c.printCredits()
    c.printBindings()
    
    # Start the controller
    c.run()
    
# Basic main call 
if __name__ == '__main__':
    main()