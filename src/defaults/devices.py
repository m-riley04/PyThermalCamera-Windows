import os
from src.models.deviceinfo import DeviceInfo

DEVICES_FOLDER_PATH = os.path.join(os.getcwd(), "devices")
DEVICE_PRINT_SPACING = 20

def loadAllSupportedDevices() -> list[DeviceInfo]:
    """
    Loads all the supported devices from the devices/ folder and returns them as a list of DeviceInfo objects.
    """
    device_files = [f for f in os.listdir(DEVICES_FOLDER_PATH) if f.endswith(".json")]
    devices = []
    for file in device_files:
        device = DeviceInfo.createFromJson(os.path.join(DEVICES_FOLDER_PATH, file))
        devices.append(device)
    return devices

def printAllSupportedDevices():
    """
    Prints all the supported devices and their specifications to the console.
    """
    print(f"All supported devices in the devices folder:")
    devices = loadAllSupportedDevices()
    for device in devices:
        print("-" * DEVICE_PRINT_SPACING)
        print(f"Name: {device.name}")
        print(f"Resolution: {device.specs.imaging.ir_resolution_width_px}x{device.specs.imaging.ir_resolution_height_px}")
        print(f"Temperature Range: {device.specs.functions.measurement_range_min_c}C to {device.specs.functions.measurement_range_max_c}C")
        print(f"Temperature Accuracy: ±{device.specs.imaging.measurement_accuracy_c}C")
        print(f"Frame Rate: {device.specs.imaging.frame_rate_hz} FPS")