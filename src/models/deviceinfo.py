from dataclasses import dataclass

@dataclass
class DeviceInfoSpecsHardware:
    system: str | None
    operating_system: str | None
    battery_capacity: int | None
    display_screen: str | None
    voltage_v: float | None
    charging_time: int | None
    battery_life: int | None
    storage: str | None
    led_flashlight: bool | None
    power_consumption_w: float | None

@dataclass
class DeviceInfoSpecsImaging:
    calib_temp_min_m: float | None
    calib_temp_max_m: float | None
    id_min_m: float | None
    id_max_m: float | None
    recog_min_m: float | None
    recog_max_m: float | None
    detect_min_m: float | None
    detect_max_m: float | None
    measurement_accuracy_c: float | None
    measurement_accuracy_pct: float | None
    ir_resolution_width_px: int | None
    ir_resolution_height_px: int | None
    focal_length_mm: float | None
    fov_h_deg: float | None
    fov_v_deg: float | None
    spectral_range_min_um: float | None
    spectral_range_max_um: float | None
    netd_mk: float | None
    temperature_resolution_c: float | None
    frame_rate_hz: int | None

@dataclass
class DeviceInfoSpecsFunctions:
    measurement_range_min_c: int | None
    measurement_range_max_c: int | None
    professional_function: str | None
    digital_zoom: bool | None
    image_modes: list[str] | None
    measuring_modes: list[str] | None
    video_recording: bool | None
    video_transfer_via_usb: bool | None
    wifi: bool | None
    pc_analysis_software: bool | None
    visible_light_camera: bool | None
    pseudo_color_palettes: list[str] | None
    pseudo_color_palette_count: int | None
    custom_color_palette: bool | None
    high_low_temp_alarms: bool | None
    auto_power_off: bool | None
    temperature_units: list[str] | None

@dataclass
class DeviceInfoSpecsOther:
    operating_temp_min_c: int | None
    operating_temp_max_c: int | None
    tripod_screw_hole: bool | None
    drop_test_height_m: float | None
    ip_rating: str | None
    certifications: list[str] | None
    gross_weight_g: int | None
    device_weight_g: int | None
    package_size_l_mm: int | None
    package_size_w_mm: int | None
    package_size_h_mm: int | None
    languages_supported_count: int | None
    languages_supported: list[str] | None

@dataclass
class DeviceInfoSpecs:
    hardware: DeviceInfoSpecsHardware | None = None
    imaging: DeviceInfoSpecsImaging | None = None
    functions: DeviceInfoSpecsFunctions | None = None
    other: DeviceInfoSpecsOther | None = None

@dataclass
class DeviceInfo:
    """
    Holds information about the thermal camera device, such as its index, resolution, and temperature range.
    NOTE: This does NOT hold values that are calculated at runtime, such as the current temperature reading or video index. This is only for static information about the device itself.
    """
    id: str
    name: str | None
    description: str | None
    manufacturer: str | None
    specs: DeviceInfoSpecs | None = None