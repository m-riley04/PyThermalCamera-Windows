from defaults.values import DEFAULT_TEMPERATURE_SIG_DIGITS
from enums.TemperatureUnitEnum import TemperatureUnit

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

def celsiusToKelvin(temperature: float) -> float:
    """
    Converts a temperature in Celsius to Kelvin.
    Formula: °C + 273.15 = K
    """
    return temperature + 273.15

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