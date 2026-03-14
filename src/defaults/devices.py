import json
import os

from src.enums.DeviceModelEnum import DeviceModel
from src.models.deviceinfo import DeviceInfo

_DEVICES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "devices"))

def loadDeviceFromJson(path: str) -> DeviceInfo:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    imaging = data["specifications"]["imaging"]
    functions = data["specifications"]["functions"]
    return DeviceInfo(
        name=data["name"],
        width=imaging["ir_resolution_x"],
        height=imaging["ir_resolution_y"],
        temp_min_c=functions["measurement_range_min_c"],
        temp_max_c=functions["measurement_range_max_c"],
        temp_accuracy_c=imaging["measurement_accuracy_c"],
        fps=imaging["frame_rate_hz"],
    )

def _load_all_devices() -> dict[DeviceModel, DeviceInfo]:
    result = {}
    for model in DeviceModel:
        json_path = os.path.join(_DEVICES_DIR, f"{model.value}.json")
        if os.path.exists(json_path):
            result[model] = loadDeviceFromJson(json_path)
    return result

# Represents the specifications for each supported device model, loaded from JSON files in devices/.
SUPPORTED_DEVICES: dict[DeviceModel, DeviceInfo] = _load_all_devices()