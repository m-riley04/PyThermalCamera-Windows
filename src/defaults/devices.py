from enums.DeviceModelEnum import DeviceModel
from models.deviceinfo import DeviceInfo

# Represents the specifications for each supported device model. 
# These can be used to initialize the program with the correct settings for each device.
SUPPORTED_DEVICES: dict[DeviceModel, DeviceInfo] = {
    DeviceModel.TC001: DeviceInfo(
        name="Topdon TC001",
        width=256,
        height=192,
        temp_min_c=-20,
        temp_max_c=550,
        temp_accuracy_c=2.0,
        fps=25
    ),
    DeviceModel.TS001: DeviceInfo(), # The default values are based on TS001, so default init.
    DeviceModel.P2_PRO: DeviceInfo(
        name="Infiray P2 Pro",
        width=256,
        height=192,
        temp_min_c=-20,
        temp_max_c=550,
        temp_accuracy_c=2.0,
        fps=25
    )
}