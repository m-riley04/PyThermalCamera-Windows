import json
from dataclasses import dataclass
from src.defaults.values import DEFAULT_NORMALIZATION_OFFSET
from src.enums.ThermalByteOrderEnum import ThermalByteOrder

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

    @staticmethod
    def createFromJson(data: dict) -> 'DeviceInfoSpecsHardware':
        return DeviceInfoSpecsHardware(
            system=data.get("system"),
            operating_system=data.get("operating_system"),
            battery_capacity=data.get("battery_capacity"),
            display_screen=data.get("display_screen"),
            voltage_v=data.get("voltage_v"),
            charging_time=data.get("charging_time"),
            battery_life=data.get("battery_life"),
            storage=data.get("storage"),
            led_flashlight=data.get("led_flashlight"),
            power_consumption_w=data.get("power_consumption_w")
        )

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

    @staticmethod
    def createFromJson(data: dict) -> 'DeviceInfoSpecsImaging':
        return DeviceInfoSpecsImaging(
            calib_temp_min_m=data.get("calib_temp_min_m"),
            calib_temp_max_m=data.get("calib_temp_max_m"),
            id_min_m=data.get("id_min_m"),
            id_max_m=data.get("id_max_m"),
            recog_min_m=data.get("recog_min_m"),
            recog_max_m=data.get("recog_max_m"),
            detect_min_m=data.get("detect_min_m"),
            detect_max_m=data.get("detect_max_m"),
            measurement_accuracy_c=data.get("measurement_accuracy_c"),
            measurement_accuracy_pct=data.get("measurement_accuracy_pct"),
            ir_resolution_width_px=data.get("ir_resolution_width_px"),
            ir_resolution_height_px=data.get("ir_resolution_height_px"),
            focal_length_mm=data.get("focal_length_mm"),
            fov_h_deg=data.get("fov_h_deg"),
            fov_v_deg=data.get("fov_v_deg"),
            spectral_range_min_um=data.get("spectral_range_min_um"),
            spectral_range_max_um=data.get("spectral_range_max_um"),
            netd_mk=data.get("netd_mk"),
            temperature_resolution_c=data.get("temperature_resolution_c"),
            frame_rate_hz=data.get("frame_rate_hz")
        )

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

    @staticmethod
    def createFromJson(data: dict) -> 'DeviceInfoSpecsFunctions':
        return DeviceInfoSpecsFunctions(
            measurement_range_min_c=data.get("measurement_range_min_c"),
            measurement_range_max_c=data.get("measurement_range_max_c"),
            professional_function=data.get("professional_function"),
            digital_zoom=data.get("digital_zoom"),
            image_modes=data.get("image_modes"),
            measuring_modes=data.get("measuring_modes"),
            video_recording=data.get("video_recording"),
            video_transfer_via_usb=data.get("video_transfer_via_usb"),
            wifi=data.get("wifi"),
            pc_analysis_software=data.get("pc_analysis_software"),
            visible_light_camera=data.get("visible_light_camera"),
            pseudo_color_palettes=data.get("pseudo_color_palettes"),
            pseudo_color_palette_count=data.get("pseudo_color_palette_count"),
            custom_color_palette=data.get("custom_color_palette"),
            high_low_temp_alarms=data.get("high_low_temp_alarms"),
            auto_power_off=data.get("auto_power_off"),
            temperature_units=data.get("temperature_units")
        )

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

    @staticmethod
    def createFromJson(data: dict) -> 'DeviceInfoSpecsOther':
        return DeviceInfoSpecsOther(
            operating_temp_min_c=data.get("operating_temp_min_c"),
            operating_temp_max_c=data.get("operating_temp_max_c"),
            tripod_screw_hole=data.get("tripod_screw_hole"),
            drop_test_height_m=data.get("drop_test_height_m"),
            ip_rating=data.get("ip_rating"),
            certifications=data.get("certifications"),
            gross_weight_g=data.get("gross_weight_g"),
            device_weight_g=data.get("device_weight_g"),
            package_size_l_mm=data.get("package_size_l_mm"),
            package_size_w_mm=data.get("package_size_w_mm"),
            package_size_h_mm=data.get("package_size_h_mm"),
            languages_supported_count=data.get("languages_supported_count"),
            languages_supported=data.get("languages_supported")
        )

@dataclass
class DeviceInfoSpecs:
    hardware: DeviceInfoSpecsHardware | None = None
    imaging: DeviceInfoSpecsImaging | None = None
    functions: DeviceInfoSpecsFunctions | None = None
    other: DeviceInfoSpecsOther | None = None

@dataclass
class DeviceInfoOther:
    thermal_byte_order: ThermalByteOrder | None = None
    normalization_offset: float = DEFAULT_NORMALIZATION_OFFSET

    @staticmethod
    def createFromJson(data: dict) -> 'DeviceInfoOther':
        thermal_byte_order_str: str | None = data.get("thermal_byte_order")
        thermal_byte_order = None
        if thermal_byte_order_str is not None:
            try:
                thermal_byte_order = ThermalByteOrder[thermal_byte_order_str]
            except KeyError:
                print(f"Warning: Invalid thermal byte order string in JSON: {thermal_byte_order_str}. Expected 'lsb0' or 'lsb1'. Defaulting to None.")

        normalization_offset = float(data.get("normalization_offset", DEFAULT_NORMALIZATION_OFFSET))
        return DeviceInfoOther(
            thermal_byte_order=thermal_byte_order
            , normalization_offset=normalization_offset
        )
    
    def __str__(self):
        return f"DeviceInfoOther(\nthermal_byte_order={self.thermal_byte_order}\n, normalization_offset={self.normalization_offset})"

@dataclass
class DeviceInfo:
    """
    Holds information about the thermal camera device, such as its index, resolution, and temperature range.
    NOTE: This does NOT hold values that are calculated at runtime, such as the current temperature reading or video index. This is only for static information about the device itself.
    """
    id: str | None
    name: str | None
    description: str | None
    manufacturer: str | None
    specs: DeviceInfoSpecs | None = None
    misc: DeviceInfoOther | None = None

    @staticmethod
    def createFromJson(path: str) -> 'DeviceInfo':
        """
        Loads device information from a JSON file at the given path. The JSON file should have a specific structure that matches the DeviceInfo dataclass.
        The JSON should have a top-level "specifications" field, which contains "hardware", "imaging", "functions", and "other" fields, each of which contains the corresponding specifications.
        The top-level JSON should also have "id", "name", "description", and "manufacturer" fields for the basic device info.
        """

        with open(path, "r", encoding="utf-8") as f:
            data: dict = json.load(f)

        specs_data: dict = data.get("specifications", {})
        specs_hw: dict = specs_data.get("hardware", {})
        specs_im: dict = specs_data.get("imaging", {})
        specs_fn: dict = specs_data.get("functions", {})
        specs_ot: dict = specs_data.get("other", {})
        mi: dict = data.get("misc", {})

        hardware = DeviceInfoSpecsHardware.createFromJson(specs_hw)
        imaging = DeviceInfoSpecsImaging.createFromJson(specs_im)
        functions = DeviceInfoSpecsFunctions.createFromJson(specs_fn)
        specsOther = DeviceInfoSpecsOther.createFromJson(specs_ot)
        misc = DeviceInfoOther.createFromJson(mi)

        # load the basic info
        id = data["id"]
        name = data.get("name")
        description = data.get("description")
        manufacturer = data.get("manufacturer")

        # load the specs
        specs = DeviceInfoSpecs(
            hardware=hardware,
            imaging=imaging,
            functions=functions,
            other=specsOther
        )

        return DeviceInfo(
            id=id,
            name=name,
            description=description,
            manufacturer=manufacturer,
            specs=specs,
            misc=misc
        )
    
    def __str__(self) -> str:
        return f"DeviceInfo(\nid={self.id}\n, name={self.name}\n, description={self.description}\n, manufacturer={self.manufacturer}\n, specs={self.specs}\n, misc={self.misc})"
