'''
Les Wright 21 June 2023
https://youtube.com/leslaboratory
A Python program to read, parse and display thermal data from the Topdon TC001 Thermal camera!

Forked by Riley Meyerkorth on 17 January 2025 to modernize and clean up the program for Windows and the TS001.
'''

from argparse import ArgumentParser
from defaults.parsers.cli_parser import parseDeviceInfoFromArgs
from defaults.values import DEFAULT_DEVICE_FPS, DEFAULT_DEVICE_NAME, DEFAULT_DEVICE_TEMP_MAX_C, DEFAULT_DEVICE_TEMP_MIN_C, DEFAULT_SENSOR_HEIGHT_PX, DEFAULT_SENSOR_WIDTH_PX, DEFAULT_VIDEO_DEVICE_INDEX
from controllers.thermalcameracontroller import ThermalCameraController

# Initialize argument parsing
parser = ArgumentParser()
parser.add_argument("-i,", "--device-index", dest="device_index", type=int, default=DEFAULT_VIDEO_DEVICE_INDEX, help=f"VideoDevice index. Default is {DEFAULT_VIDEO_DEVICE_INDEX}.")
parser.add_argument("--temp-max", dest="temp_max", type=int, default=DEFAULT_DEVICE_TEMP_MAX_C, help=f"Maximum temperature readable by the device in Celsius. Default is {DEFAULT_DEVICE_TEMP_MAX_C}.")
parser.add_argument("--temp-min", dest="temp_min", type=int, default=DEFAULT_DEVICE_TEMP_MIN_C, help=f"Minimum temperature readable by the device in Celsius. Default is {DEFAULT_DEVICE_TEMP_MIN_C}.")
parser.add_argument("--width", dest="width", type=int, default=DEFAULT_SENSOR_WIDTH_PX, help=f"Width of the sensor in pixels. Default is {DEFAULT_SENSOR_WIDTH_PX}.")
parser.add_argument("--height", dest="height", type=int, default=DEFAULT_SENSOR_HEIGHT_PX, help=f"Height of the sensor in pixels. Default is {DEFAULT_SENSOR_HEIGHT_PX}.")
parser.add_argument("-f", "--frame-rate", dest="frame_rate", type=int, default=DEFAULT_DEVICE_FPS, help=f"Frame rate of the device. Default is {DEFAULT_DEVICE_FPS} FPS.")
parser.add_argument("-n", "--device-name", dest="device_name", type=str, default=DEFAULT_DEVICE_NAME, help=f"Name of the device. Default is {DEFAULT_DEVICE_NAME}.")
args = parser.parse_args()

def main():
    # parse info from args
    device_info = parseDeviceInfoFromArgs(args)
        
    # Initialize the controller
    c = ThermalCameraController(device_info)
    
    # Print the credits and bindings
    c.printCredits()
    c.printBindings()
    
    # Start the controller
    c.run()
    
# Basic main call 
if __name__ == '__main__':
    main()