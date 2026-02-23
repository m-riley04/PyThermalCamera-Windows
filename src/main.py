'''
Les Wright 21 June 2023
https://youtube.com/leslaboratory
A Python program to read, parse and display thermal data from the Topdon TC001 Thermal camera!

Forked by Riley Meyerkorth on 17 January 2025 to modernize and clean up the program for Windows and the TS001.
'''

from parsers.cli_parser import createParser, parseDeviceInfoFromArgs
from defaults.values import DEFAULT_VIDEO_DEVICE_INDEX
from controllers.thermalcameracontroller import ThermalCameraController

# Initialize argument parsing
parser = createParser()
args = parser.parse_args()

def main():
    # get device index
    device_index = getattr(args, 'device_index', DEFAULT_VIDEO_DEVICE_INDEX)

    # parse info from args
    device_info = parseDeviceInfoFromArgs(args)
        
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