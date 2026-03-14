import json, os
from src.models.deviceinfo import DeviceInfo, DeviceInfoSpecs, DeviceInfoSpecsHardware, DeviceInfoSpecsImaging, DeviceInfoSpecsFunctions, DeviceInfoSpecsOther

DEVICES_FOLDER_PATH = os.path.join(os.getcwd(), "devices")

def loadDeviceFromJson(path: str) -> DeviceInfo:
    """
    Loads a device object from a JSON file
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    specs_data = data.get("specifications", {})
    hw = specs_data.get("hardware", {})
    im = specs_data.get("imaging", {})
    fn = specs_data.get("functions", {})
    ot = specs_data.get("other", {})

    hardware = DeviceInfoSpecsHardware(
        system=hw.get("system"),
        operating_system=hw.get("operating_system"),
        battery_capacity=hw.get("battery_capacity"),
        display_screen=hw.get("display_screen"),
        voltage_v=hw.get("voltage_v"),
        charging_time=hw.get("charging_time"),
        battery_life=hw.get("battery_life"),
        storage=hw.get("storage"),
        led_flashlight=hw.get("led_flashlight"),
        power_consumption_w=hw.get("power_consumption_w"),
    )
    imaging = DeviceInfoSpecsImaging(
        calib_temp_min_m=im.get("calib_temp_min_m"),
        calib_temp_max_m=im.get("calib_temp_max_m"),
        id_min_m=im.get("id_min_m"),
        id_max_m=im.get("id_max_m"),
        recog_min_m=im.get("recog_min_m"),
        recog_max_m=im.get("recog_max_m"),
        detect_min_m=im.get("detect_min_m"),
        detect_max_m=im.get("detect_max_m"),
        measurement_accuracy_c=im.get("measurement_accuracy_c"),
        measurement_accuracy_pct=im.get("measurement_accuracy_pct"),
        ir_resolution_width_px=im.get("ir_resolution_width_px"),
        ir_resolution_height_px=im.get("ir_resolution_height_px"),
        focal_length_mm=im.get("focal_length_mm"),
        fov_h_deg=im.get("fov_h_deg"),
        fov_v_deg=im.get("fov_v_deg"),
        spectral_range_min_um=im.get("spectral_range_min_um"),
        spectral_range_max_um=im.get("spectral_range_max_um"),
        netd_mk=im.get("netd_mk"),
        temperature_resolution_c=im.get("temperature_resolution_c"),
        frame_rate_hz=im.get("frame_rate_hz"),
    )
    functions = DeviceInfoSpecsFunctions(
        measurement_range_min_c=fn.get("measurement_range_min_c"),
        measurement_range_max_c=fn.get("measurement_range_max_c"),
        professional_function=fn.get("professional_function"),
        digital_zoom=fn.get("digital_zoom"),
        image_modes=fn.get("image_modes"),
        measuring_modes=fn.get("measuring_modes"),
        video_recording=fn.get("video_recording"),
        video_transfer_via_usb=fn.get("video_transfer_via_usb"),
        wifi=fn.get("wifi"),
        pc_analysis_software=fn.get("pc_analysis_software"),
        visible_light_camera=fn.get("visible_light_camera"),
        pseudo_color_palettes=fn.get("pseudo_color_palettes"),
        pseudo_color_palette_count=fn.get("pseudo_color_palette_count"),
        custom_color_palette=fn.get("custom_color_palette"),
        high_low_temp_alarms=fn.get("high_low_temp_alarms"),
        auto_power_off=fn.get("auto_power_off"),
        temperature_units=fn.get("temperature_units"),
    )
    other = DeviceInfoSpecsOther(
        operating_temp_min_c=ot.get("operating_temp_min_c"),
        operating_temp_max_c=ot.get("operating_temp_max_c"),
        tripod_screw_hole=ot.get("tripod_screw_hole"),
        drop_test_height_m=ot.get("drop_test_height_m"),
        ip_rating=ot.get("ip_rating"),
        certifications=ot.get("certifications"),
        gross_weight_g=ot.get("gross_weight_g"),
        device_weight_g=ot.get("device_weight_g"),
        package_size_l_mm=ot.get("package_size_l_mm"),
        package_size_w_mm=ot.get("package_size_w_mm"),
        package_size_h_mm=ot.get("package_size_h_mm"),
        languages_supported_count=ot.get("languages_supported_count"),
        languages_supported=ot.get("languages_supported"),
    )

    return DeviceInfo(
        id=data["id"],
        name=data.get("name"),
        description=data.get("description"),
        manufacturer=data.get("manufacturer"),
        specs=DeviceInfoSpecs(hardware=hardware, imaging=imaging, functions=functions, other=other),
    )

def loadAllSupportedDevices() -> list[DeviceInfo]:
    """
    Loads all the supported devices from the devices/ folder and returns them as a list of DeviceInfo objects.
    """
    device_files = [f for f in os.listdir(DEVICES_FOLDER_PATH) if f.endswith(".json")]
    devices = []
    for file in device_files:
        device = loadDeviceFromJson(os.path.join(DEVICES_FOLDER_PATH, file))
        devices.append(device)
    return devices

def printAllSupportedDevices():
    """
    Prints all the supported devices and their specifications to the console.
    """
    print(f"All supported devices in the devices folder:")
    devices = loadAllSupportedDevices()
    for device in devices:
        print("-" * 20)
        print(f"Name: {device.name}")
        print(f"Resolution: {device.specs.imaging.ir_resolution_width_px}x{device.specs.imaging.ir_resolution_height_px}")
        print(f"Temperature Range: {device.specs.functions.measurement_range_min_c}C to {device.specs.functions.measurement_range_max_c}C")
        print(f"Temperature Accuracy: ±{device.specs.functions.measurement_accuracy_c}C")
        print(f"Frame Rate: {device.specs.imaging.frame_rate_hz} FPS")