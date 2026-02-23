from enum import Enum

class DeviceModel(Enum):
    """
    Thermal camera device models with their specifications.
    Based on research from EEVBlog forum and manufacturer specs.
    """
    TC001 = "TC001"  # Topdon TC001
    TS001 = "TS001"  # Topdon TS001
    P2_PRO = "P2_PRO"  # Infiray P2 Pro
    
    # Add more models as discovered/tested

class DeviceSpecs:
    """Specifications for supported thermal camera models."""
    
    SPECS = {
        DeviceModel.TC001: {
            "name": "Topdon TC001",
            "width_px": 256,
            "height_px": 192,
            "fps": 25,
            "temp_min_c": -20,
            "temp_max_c": 550,
            "temp_accuracy_c": 2.0,  # ±2°C or 2% of max
            "raw_to_celsius": lambda raw: (raw / 64.0) - 273.15,
            "note": "Standard Topdon TC001. Formula: (raw/64) - 273.15"
        },
        DeviceModel.TS001: {
            "name": "Topdon TS001",
            "width_px": 256,
            "height_px": 192,
            "fps": 25,
            "temp_min_c": -20,
            "temp_max_c": 550,
            "temp_accuracy_c": 2.0,
            "raw_to_celsius": lambda raw: (raw / 64.0) - 273.15,
            "note": "Topdon TS001. Same sensor/formula as TC001."
        },
        DeviceModel.P2_PRO: {
            "name": "Infiray P2 Pro",
            "width_px": 256,
            "height_px": 192,
            "fps": 25,
            "temp_min_c": -20,
            "temp_max_c": 550,
            "temp_accuracy_c": 2.0,
            "raw_to_celsius": lambda raw: (raw / 64.0) - 273.15,
            "note": "Infiray P2 Pro. Uses same formula, confirmed by LeoDJ reverse-engineering."
        }
    }
    
    @staticmethod
    def get_specs(model: DeviceModel) -> dict:
        """Get specifications for a device model."""
        if model not in DeviceSpecs.SPECS:
            # Default to TC001 if unknown
            return DeviceSpecs.SPECS[DeviceModel.TC001]
        return DeviceSpecs.SPECS[model]
    
    @staticmethod
    def get_temp_conversion_func(model: DeviceModel):
        """Get the temperature conversion function for a device."""
        specs = DeviceSpecs.get_specs(model)
        return specs["raw_to_celsius"]
