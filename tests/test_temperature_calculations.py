import os
import sys
import unittest

import numpy as np


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_ROOT = os.path.join(PROJECT_ROOT, "src")

if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)

from controllers.thermalcameracontroller import ThermalCameraController
from defaults.thermal_values import SENSOR_WIDTH
from enums.TemperatureUnitEnum import TemperatureUnit
from helpers.conversions import convertTemperatureDeltaForDisplay, convertTemperatureForDisplay


class TemperatureCalculationTests(unittest.TestCase):
    def setUp(self):
        self.controller = ThermalCameraController.__new__(ThermalCameraController)
        self.controller._width = SENSOR_WIDTH
        self.controller._height = 192
        self.controller._didLogFrameLayoutWarning = False

    def test_normalize_temperature(self):
        normalized = self.controller.normalizeTemperature(rawTemp=19200)
        self.assertAlmostEqual(normalized, 26.85, places=2)

    def test_calculate_raw_temperature_from_center_pixel(self):
        thdata = np.zeros((192, 256, 3), dtype=np.uint8)
        thdata[96, 128, 0] = 10
        thdata[96, 128, 1] = 2

        raw = self.controller.calculateRawTemperature(thdata)

        self.assertEqual(raw, 522)

    def test_calculate_average_temperature(self):
        thdata = np.zeros((192, 256, 3), dtype=np.uint8)
        thdata[..., 0] = 10
        thdata[..., 1] = 2

        avg_temp = self.controller.calculateAverageTemperature(thdata)

        expected = round(((2 * 256 + 10) / 64) - 273.15, 2)
        self.assertEqual(avg_temp, expected)

    def test_calculate_minimum_temperature_tracks_position(self):
        thdata = np.zeros((192, 256, 3), dtype=np.uint8)
        thdata[..., 1] = 5
        thdata[20, 30, 1] = 1
        thdata[20, 30, 0] = 7

        min_temp = self.controller.calculateMinimumTemperature(thdata)

        expected = round(((1 * 256 + 7) / 64) - 273.15, 2)
        self.assertEqual(min_temp, expected)
        self.assertEqual((self.controller._lcol, self.controller._lrow), (20, 30))

    def test_calculate_maximum_temperature_tracks_position(self):
        thdata = np.zeros((192, 256, 3), dtype=np.uint8)
        thdata[..., 1] = 25
        thdata[80, 100, 1] = 200
        thdata[80, 100, 0] = 9

        max_temp = self.controller.calculateMaximumTemperature(thdata)

        expected = round(((200 * 256 + 9) / 64) - 273.15, 2)
        self.assertEqual(max_temp, expected)
        self.assertEqual((self.controller._mcol, self.controller._mrow), (80, 100))

    def test_convert_temperature_for_display_fahrenheit(self):
        converted = convertTemperatureForDisplay(0, TemperatureUnit.FAHRENHEIT)
        self.assertEqual(converted, 32.0)

    def test_convert_temperature_delta_for_display_fahrenheit(self):
        converted = convertTemperatureDeltaForDisplay(2, TemperatureUnit.FAHRENHEIT)
        self.assertEqual(converted, 3.6)

    def test_split_frame_data_handles_padded_flattened_buffer(self):
        paddedWidth = 264
        totalRows = self.controller._height * 2
        flatSize = totalRows * paddedWidth * 2
        frame = np.zeros((1, flatSize), dtype=np.uint8)

        # Lower half contains thermal data; write center thermal bytes for expected raw temp.
        thermalCenterRow = self.controller._height + (self.controller._height // 2)
        thermalCenterCol = self.controller._width // 2
        baseIndex = ((thermalCenterRow * paddedWidth) + thermalCenterCol) * 2
        frame[0, baseIndex] = 10
        frame[0, baseIndex + 1] = 2

        imdata, thdata = self.controller._splitFrameData(frame)

        self.assertEqual(imdata.shape, (192, 256, 2))
        self.assertEqual(thdata.shape, (192, 256, 2))
        self.assertEqual(self.controller.calculateRawTemperature(thdata), 522)


if __name__ == "__main__":
    unittest.main()
