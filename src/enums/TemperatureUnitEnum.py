from enum import Enum

class TemperatureUnit(Enum):
    CELSIUS = 0
    FAHRENHEIT = 1
    KELVIN = 2

def getSymbolFromTempUnit(unit: TemperatureUnit) -> str:
    if unit == TemperatureUnit.FAHRENHEIT:
        return "F"
    elif unit == TemperatureUnit.KELVIN:
        return "K"
    else:
        return "C"
    
def getTempUnitFromString(unitStr: str) -> TemperatureUnit:
    unit = unitStr.strip().lower()
    if unit in ("f", "fahrenheit"):
        return TemperatureUnit.FAHRENHEIT
    elif unit in ("k", "kelvin"):
        return TemperatureUnit.KELVIN
    elif unit in ("c", "celsius"):
        return TemperatureUnit.CELSIUS
    else:
        raise ValueError(f"Invalid temperature unit string: {unitStr}")