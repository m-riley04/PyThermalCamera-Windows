'''
Les Wright 21 June 2023
https://youtube.com/leslaboratory
A Python program to read, parse and display thermal data from the Topdon TC001 Thermal camera!

Forked by Riley Meyerkorth on 17 January 2025 to modernize and clean up the program for Windows and the TS001.
'''

from argparse import ArgumentParser
from defaults.values import VIDEO_DEVICE_INDEX
from controllers.thermalcameracontroller import ThermalCameraController

# Initialize argument parsing
parser = ArgumentParser()
parser.add_argument("--device", type=int, default=VIDEO_DEVICE_INDEX, help=f"VideoDevice index. Default is {VIDEO_DEVICE_INDEX}.")
args = parser.parse_args()

def main():
    # Check for devices
    if args.device:
        dev = args.device
    else:
        dev = VIDEO_DEVICE_INDEX
        
    # Initialize the controller
    c = ThermalCameraController(deviceIndex=dev)
    
    # Print the credits and bindings
    c.printCredits()
    c.printBindings()
    
    # Start the controller
    c.run()
    
# Basic main call 
if __name__ == '__main__':
    main()