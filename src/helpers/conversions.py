from src.defaults.values import DEFAULT_NORMALIZATION_OFFSET, DEFAULT_TEMPERATURE_SIG_DIGITS
from src.enums.TemperatureUnitEnum import TemperatureUnit

# NOTE: most of these conversions are from celsius to x. This is because the data is stored as celsius.

def celsiusToFahrenheit(temperature: float) -> float:
    """
    Converts a temperature in Celsius to Fahrenheit.
    Formula: (°C x 9/5) + 32 = °F
    """
    return (temperature * 9.0 / 5.0) + 32.0

def celsiusDeltaToFahrenheitDelta(temperatureDelta: float) -> float:
    """
    Converts a temperature delta in Celsius to a temperature delta in Fahrenheit.
    Since this is a delta, we only apply the multiplication factor, not the addition.
    """
    return temperatureDelta * 9.0 / 5.0

def celsiusToKelvin(temperature: float, offset: float = DEFAULT_NORMALIZATION_OFFSET) -> float:
    """
    Converts a temperature in Celsius to Kelvin.
    Formula: °C + 273.15 = K
    """
    return temperature + offset

def convertTemperatureForDisplay(temperatureCelsius: float, temperatureUnit: TemperatureUnit) -> float:
    """
    Converts the temperature to the appropriate unit for display based on the user's preference.
    """
    if temperatureUnit == TemperatureUnit.FAHRENHEIT:
        return round(celsiusToFahrenheit(temperatureCelsius), DEFAULT_TEMPERATURE_SIG_DIGITS)
    elif temperatureUnit == TemperatureUnit.KELVIN:
        return round(celsiusToKelvin(temperatureCelsius), DEFAULT_TEMPERATURE_SIG_DIGITS)
    return temperatureCelsius

def convertTemperatureDeltaForDisplay(temperatureDeltaCelsius: float, temperatureUnit: TemperatureUnit) -> float:
    """
    Converts the temperature delta to the appropriate unit for display based on the user's preference.
    """
    if temperatureUnit == TemperatureUnit.FAHRENHEIT:
        return round(celsiusDeltaToFahrenheitDelta(temperatureDeltaCelsius), DEFAULT_TEMPERATURE_SIG_DIGITS)
    elif temperatureUnit == TemperatureUnit.KELVIN:
        return round(temperatureDeltaCelsius, DEFAULT_TEMPERATURE_SIG_DIGITS)  # Delta is the same in Celsius and Kelvin
    return temperatureDeltaCelsius