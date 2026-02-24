'''
Les Wright 21 June 2023
https://youtube.com/leslaboratory
A Python program to read, parse and display thermal data from the Topdon TC001 Thermal camera!

Forked by Riley Meyerkorth on 17 January 2025 to modernize and clean up the program for Windows and the TS001.
'''

from enums.DeviceModelEnum import DeviceModel
from helpers.deviceHelper import getInfoByModel, getModelByName, printAllVideoDevices
from parsers.cli_parser import createParser, parseDeviceInfoFromArgs
from defaults.values import DEFAULT_VIDEO_DEVICE_INDEX
from controllers.thermalcameracontroller import ThermalCameraController

# Initialize argument parsing
parser = createParser()
args = parser.parse_args()

def main():
    print(args)

    subcommand = getattr(args, 'subcommand', None)
    if subcommand is None:
        parser.print_help()
        return

    device_info = None
    if subcommand == "list":
        # This case is handled by the set_defaults func of the list subcommand, so we just return after it executes.
        printAllVideoDevices()
        return
    
    if subcommand == "manual":
        # parse info from args
        device_info = parseDeviceInfoFromArgs(args)
    elif subcommand == "model":
        modelName = getattr(args, 'model', None)
        if modelName is None:
            print("Error: Model name is required when using the model subcommand.")
            return
        device_info = getInfoByModel(getModelByName(modelName) or DeviceModel.TC001)

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