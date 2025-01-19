'''
Les Wright 21 June 2023
https://youtube.com/leslaboratory
A Python program to read, parse and display thermal data from the Topdon TC001 Thermal camera!

Forked by Riley Meyerkorth on 17 January 2025 to modernize and clean up the program for Windows and the TS001.
'''

import argparse
from controllers.thermalcameracontroller import ThermalCameraController

# Initialize argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--device", type=int, default=0, help=f"VideoDevice index. Default is 0.")
args = parser.parse_args()

def main():
    # Check for devices
    if args.device:
        dev = args.device
    else:
        dev = 1
        
    # Initialize the controller
    c = ThermalCameraController(
        deviceIndex=dev,
        deviceName="TS001",
        )
    
    # Print the credits and bindings
    c.printCredits()
    c.printBindings()
    
    # Start the controller
    c.run()
    
           
# Basic main call 
if __name__ == '__main__':
    main()