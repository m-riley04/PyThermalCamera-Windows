import logging

import cv2, time, os, sys, numpy as np
from numpy.typing import NDArray
from src.enums.ThermalByteOrderEnum import ThermalByteOrder
from src.defaults.values import *
from src.defaults.keybinds import *
from src.enums.ColormapEnum import Colormap
from src.controllers.guiController import GuiController
from src.enums.TemperatureUnitEnum import TemperatureUnit, getSymbolFromTempUnit
from src.helpers.conversions import convertTemperatureDeltaForDisplay, convertTemperatureForDisplay
from src.models.deviceinfo import DeviceInfo
from src.models.envinfo import EnvInfo

class ThermalCameraController:
    def __init__(self, 
                 device: DeviceInfo,
                 logger: logging.Logger,
                 device_index: int = DEFAULT_VIDEO_DEVICE_INDEX,
                 environment: EnvInfo = EnvInfo(),
                 mediaOutputPath: str = DEFAULT_MEDIA_OUTPUT_PATH,
                 temperatureUnit: TemperatureUnit = TemperatureUnit.CELSIUS):
        self.logger = logger
        self.logger.info(f"Initializing ThermalCameraController for device '{device.name}' at index {device_index}")
        
        # Parameters init
        self._deviceInfo: DeviceInfo = device
        self._deviceIndex: int = device_index
        self._env: EnvInfo = environment
        self._temperatureUnit: TemperatureUnit = temperatureUnit
        self._temperatureUnitSymbol: str = getSymbolFromTempUnit(self._temperatureUnit)

        # Log if rpi is detected
        if self._env.isPi:
            self.logger.info("Detected Raspberry Pi environment.")

        # Calculated values init
        self._rawTemp = DEFAULT_TEMPERATURE_RAW
        self._temp = DEFAULT_TEMPERATURE
        self._maxTemp = DEFAULT_TEMPERATURE_MAX
        self._minTemp = DEFAULT_TEMPERATURE_MIN
        self._avgTemp = DEFAULT_TEMPERATURE_AVG
        self._mcol: int = 0
        self._mrow: int = 0
        self._lcol: int = 0
        self._lrow: int = 0
        
        # Media/recording init
        self._isRecording = DEFAULT_RECORDING_STATE
        self._mediaOutputPath: str = mediaOutputPath
        
        if not os.path.exists(self._mediaOutputPath):
            self.logger.info(f"Media output path '{self._mediaOutputPath}' does not exist. Creating directory.")
            os.makedirs(self._mediaOutputPath)
        
        # GUI Init
        self._guiController = GuiController(
            logger=logger.getChild("GuiController")
            , width=self._deviceInfo.specs.imaging.ir_resolution_width_px
            , height=self._deviceInfo.specs.imaging.ir_resolution_height_px
            , temperatureUnit=self._temperatureUnit)
        
        # OpenCV init
        self._cap = None
        self._videoOut = None
        self._didLogFrameLayoutWarning = False
        self._captureBackend = None
        self._didLogThermalByteOrder = False

        self.logger.info("ThermalCameraController initialized successfully")
        self.logger.debug(f"Device Info: {self._deviceInfo}")

    def _rawFromBytes(self, byte0: int, byte1: int) -> int:
        """
        Combine two uint8 bytes into a 16-bit raw temperature sample.

        The original TC001 script treats channel 0 as the LSB and channel 1 as the MSB.
        Some Windows capture paths/backends can swap this ordering, so we allow autodetection.
        """
        self.logger.debug(f"Combining bytes into raw temperature with byte0={byte0}, byte1={byte1}, thermal_byte_order={self._deviceInfo.misc.thermal_byte_order}")
        if self._deviceInfo.misc.thermal_byte_order == ThermalByteOrder.LSB_BYTE_1:
            return int(byte1) + (int(byte0) << 8)
        return int(byte0) + (int(byte1) << 8)
    
    def is_plausible_celsius(self, temp: float) -> bool:
        """
        Checks if a temperature is within a plausible range for Celsius temperatures that the device should be able to read.
        Used primarily for autodetecting byte order and errors in data.
        """
        isPlausible = self._deviceInfo.specs.functions.measurement_range_min_c <= temp <= self._deviceInfo.specs.functions.measurement_range_max_c
        if not isPlausible and not self._didLogThermalByteOrder:
            self.logger.warning(
                f"Temperature {temp}°C is outside plausible range for device '{self._deviceInfo.name}' "
                f"({self._deviceInfo.specs.functions.measurement_range_min_c}°C to {self._deviceInfo.specs.functions.measurement_range_max_c}°C). "
                "This may indicate an incorrect thermal byte order or an issue with the data. "
                "If you are seeing incorrect temperatures, try changing the byte order setting for this device."
            )
            self._didLogThermalByteOrder = True
        return isPlausible

    @staticmethod
    def printBindings():
        """
        Print key bindings for the program.
        """
        print('Key Bindings:\n')
        print(f'{KEY_INCREASE_BLUR} {KEY_DECREASE_BLUR}: Increase/Decrease Blur')
        print(f'{KEY_INCREASE_FLOATING_HIGH_LOW_TEMP_LABEL_THRESHOLD} {KEY_DECREASE_FLOATING_HIGH_LOW_TEMP_LABEL_THRESHOLD}: Floating High and Low Temp Label Threshold')
        print(f'{KEY_INCREASE_SCALE} {KEY_DECREASE_SCALE}: Change Interpolated scale Note: This will not change the window size on the Pi')
        print(f'{KEY_INCREASE_CONTRAST} {KEY_DECREASE_CONTRAST}: Contrast')
        print(f'{KEY_FULLSCREEN} {KEY_WINDOWED}: Fullscreen Windowed (note going back to windowed does not seem to work on the Pi!)')
        print(f'{KEY_RECORD} {KEY_STOP}: Record and Stop')
        print(f'{KEY_SNAPSHOT} : Snapshot')
        print(f'{KEY_CYCLE_THROUGH_COLORMAPS} : Cycle through ColorMaps')
        print(f'{KEY_INVERT} : Invert ColorMap')
        print(f'{KEY_TOGGLE_HUD} : Toggle HUD')
        print(f'{KEY_TOGGLE_TEMP_UNIT} : Toggle Celsius/Fahrenheit')
        print(f'{KEY_TOGGLE_OUTPUT_MODE} : Swap Frame Halves (fixes wrong half displaying)')
        print(f'{KEY_TOGGLE_PIP} : Toggle Picture-in-Picture Window')
        print(f'{KEY_QUIT} : Quit')

    @staticmethod
    def printCredits():
        """
        Print credits/author(s) for the program.
        """
        print('Original Author: Les Wright 21 June 2023')
        print('https://youtube.com/leslaboratory')
        print('Fork Author: Riley Meyerkorth 17 January 2025')
        print('A Python program to read, parse and display thermal data from the Topdon TC001 and TS001 Thermal cameras!\n')
    
    def _checkForKeyPress(self, keyPress: int, img):
        """
        Checks and acts on key presses. Calls upon the GUI controller to handle GUI-related key presses, and handles recording and snapshot key presses itself since they involve media controls in addition to GUI changes.
        TODO/CONSIDER: move recording controls and ALL keypresses to gui controller?
        """
        self._guiController.handleKeyPresses(keyPress, self._deviceInfo)

        ### Temp Units
        if keyPress == ord(KEY_TOGGLE_TEMP_UNIT): # Toggle temperature unit
            if self._temperatureUnit == TemperatureUnit.CELSIUS:
                self._temperatureUnit = TemperatureUnit.FAHRENHEIT
            elif self._temperatureUnit == TemperatureUnit.FAHRENHEIT:
                self._temperatureUnit = TemperatureUnit.KELVIN
            else:
                self._temperatureUnit = TemperatureUnit.CELSIUS

            self._temperatureUnitSymbol = getSymbolFromTempUnit(self._temperatureUnit)
            self.logger.info("Temperature unit changed to %s", self._temperatureUnit.name)
            self._guiController.temperatureUnitSymbol = self._temperatureUnitSymbol
        
        ### RECORDING/MEDIA CONTROLS
        if keyPress == ord(KEY_RECORD) and self._isRecording == False: # Start recording
            self._videoOut = self._record()
            self._isRecording = DEFAULT_RECORDING_STATE
            self._guiController.recordingStartTime = time.time()
            
        if keyPress == ord(KEY_STOP): # Stop recording
            self._isRecording = not DEFAULT_RECORDING_STATE
            self._guiController.recordingDuration = DEFAULT_RECORDING_DURATION

        if keyPress == ord(KEY_SNAPSHOT): # Take a snapshot
            self._guiController.last_snapshot_time = self._snapshot(img)

    def _record(self):
        """
        Start recording video to file.
        """
        self.logger.info("Starting recording...")

        currentTimeStr = time.strftime("%Y%m%d--%H%M%S")
        #do NOT use mp4 here, it is flakey!
        self._videoOut = cv2.VideoWriter(
            f"{self._mediaOutputPath}/{currentTimeStr}-output.avi",
            cv2.VideoWriter_fourcc(*'YUY2'),
            self._deviceInfo.fps,
            (self._guiController.scaledWidth, self._guiController.scaledHeight))
        return self._videoOut
    
    def _snapshot(self, img):
        """
        Takes a snapshot of the current frame.
        """
        self.logger.info("Taking snapshot...")
        #I would put colons in here, but it Win throws a fit if you try and open them!
        currentTimeStr = time.strftime("%Y%m%d-%H%M%S") 
        self._guiController.last_snapshot_time = time.strftime("%H:%M:%S")
        if not cv2.imwrite(f"{self._mediaOutputPath}/{self._deviceInfo.name}-{currentTimeStr}.png", img):
            self.logger.error("Failed to save snapshot.")
        else:
            self.logger.info(f"Snapshot saved to {self._mediaOutputPath}/{self._deviceInfo.name}-{currentTimeStr}.png")
        return self._guiController.last_snapshot_time

    def normalizeTemperature(self, rawTemp: float, d: int = DEFAULT_NORMALIZATION_DIVISOR, c: float = DEFAULT_NORMALIZATION_OFFSET) -> float:
        """
        Normalizes/converts the raw temperature data using the formula found by LeoDJ.
        Link: https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/200/
        """
        self.logger.debug(f"Normalizing temperature with rawTemp={rawTemp}, rawTemp/d={rawTemp/d}, d={d}, c={c}")
        return (rawTemp/d) - c

    def calculateTemperature(self, thdata: NDArray) -> float:
        """
        Calculates the (normalized) temperature of the frame.
        """
        raw = self.calculateRawTemperature(thdata)
        return round(self.normalizeTemperature(raw, d=self._deviceInfo.misc.normalization_divisor, c=self._deviceInfo.misc.normalization_offset), DEFAULT_TEMPERATURE_SIG_DIGITS)

    def calculateRawTemperature(self, thdata: NDArray) -> float:
        """
        Calculates the raw temperature of the center of the frame.
        """
        self.logger.debug(f"Calculating raw temperature from thermal data with shape {thdata.shape} and dtype {thdata.dtype}")
        if thdata.size == 0 or thdata.shape[0] == 0 or thdata.shape[1] == 0:
            self.logger.warning("Thermal data is empty or has invalid shape. Returning default raw temperature.")
            return DEFAULT_TEMPERATURE_RAW

        centerRow = thdata.shape[0] // 2
        centerCol = thdata.shape[1] // 2
        b0 = int(thdata[centerRow, centerCol, 0])
        b1 = int(thdata[centerRow, centerCol, 1])
        return self._rawFromBytes(b0, b1)

    def calculateAverageTemperature(self, thdata: NDArray) -> float:
        """
        Calculates the average temperature of the frame.
        """
        self.logger.debug(f"Calculating average temperature from thermal data with shape {thdata.shape} and dtype {thdata.dtype}")
        if thdata is None or thdata.size == 0 or thdata.ndim < 3 or thdata.shape[2] < 2:
            self.logger.warning("Thermal data is empty or has invalid shape. Returning default average temperature.")
            return DEFAULT_TEMPERATURE_AVG

        b0avg = int(thdata[..., 0].mean())
        b1avg = int(thdata[..., 1].mean())
        raw = self._rawFromBytes(b0avg, b1avg)
        return round(self.normalizeTemperature(raw, d=self._deviceInfo.misc.normalization_divisor, c=self._deviceInfo.misc.normalization_offset), DEFAULT_TEMPERATURE_SIG_DIGITS)

    def calculateMinimumTemperature(self, thdata: NDArray) -> float:
        """
        Calculates the minimum temperature of the frame.
        """
        self.logger.debug(f"Calculating minimum temperature from thermal data with shape {thdata.shape} and dtype {thdata.dtype}")

        # Find the min temperature in the frame
        posmin = int(thdata[...,1].argmin())
        
        # Since argmax returns a linear index, convert back to row and col
        width = thdata.shape[1]
        self._lcol, self._lrow = divmod(posmin, width)
        b0 = int(thdata[self._lcol, self._lrow, 0])
        b1 = int(thdata[self._lcol, self._lrow, 1])
        raw = self._rawFromBytes(b0, b1)

        return round(self.normalizeTemperature(raw, d=self._deviceInfo.misc.normalization_divisor, c=self._deviceInfo.misc.normalization_offset), DEFAULT_TEMPERATURE_SIG_DIGITS)

    def calculateMaximumTemperature(self, thdata: NDArray) -> float:
        """
        Calculates the maximum temperature of the frame.
        """
        self.logger.debug(f"Calculating maximum temperature from thermal data with shape {thdata.shape} and dtype {thdata.dtype}")

        # Find the max temperature in the frame
        lomax = int(thdata[...,1].max())
        posmax = int(thdata[...,1].argmax())

        # Since argmax returns a linear index, convert back to row and col
        width = thdata.shape[1]
        self._mcol, self._mrow = divmod(posmax, width)
        b0 = int(thdata[self._mcol, self._mrow, 0])
        b1 = int(thdata[self._mcol, self._mrow, 1])
        raw = self._rawFromBytes(b0, b1)

        return round(self.normalizeTemperature(raw, d=self._deviceInfo.misc.normalization_divisor, c=self._deviceInfo.misc.normalization_offset), DEFAULT_TEMPERATURE_SIG_DIGITS)

    def _splitFrameData(self, frame: NDArray, *, logWarnings: bool = True) -> tuple[NDArray | None, NDArray | None]:
        """
        Splits frame into visible-image and thermal-data halves, handling backend-specific layouts.
        """
        self.logger.debug(f"Splitting frame data with shape {frame.shape} and dtype {frame.dtype}")
        if frame is None or frame.size == 0:
            self.logger.warning("Received empty frame. Cannot split frame data.")
            return None, None

        parsedFrame = frame

        # If OpenCV has already converted to BGR/RGB (3 channels) we can no longer recover thermal bytes.
        # Fail fast with a clear warning rather than producing nonsense temperatures.
        if parsedFrame.ndim == 3 and parsedFrame.shape[2] != 2:
            if logWarnings and not self._didLogFrameLayoutWarning:
                self.logger.warning(
                    "OpenCV returned a converted frame (not raw YUY2). "
                    f"shape={parsedFrame.shape}, dtype={parsedFrame.dtype}. "
                    "Thermal bytes are not available; try a different backend (DSHOW vs MSMF) or disable RGB conversion."
                )
                self._didLogFrameLayoutWarning = True
            return None, None

        totalRows = self._deviceInfo.specs.imaging.ir_resolution_height_px * 2

        # Some Linux/V4L2 paths can expose packed YUY2 as a 2D uint16 image
        # where each uint16 encodes the two bytes we need for thermal decoding.
        if parsedFrame.ndim == 2 and parsedFrame.dtype == np.uint16:
            rows, cols = parsedFrame.shape
            if rows >= totalRows and cols >= self._deviceInfo.specs.imaging.ir_resolution_width_px:
                parsedFrame = parsedFrame.view(np.uint8).reshape(rows, cols, 2)

        # Some backends return flattened buffers (often with padded row stride).
        if parsedFrame.ndim == 2:
            flattened = parsedFrame.reshape(-1)
            if flattened.size % totalRows == 0:
                bytesPerRow = flattened.size // totalRows
                if bytesPerRow % 2 == 0:
                    pixelsPerRow = bytesPerRow // 2
                    if pixelsPerRow >= self._deviceInfo.specs.imaging.ir_resolution_width_px:
                        parsedFrame = flattened.reshape((totalRows, pixelsPerRow, 2))
                        parsedFrame = parsedFrame[:, :self._deviceInfo.specs.imaging.ir_resolution_width_px, :]

        if parsedFrame.ndim == 3 and parsedFrame.shape[0] >= totalRows:
            imageData = parsedFrame[:self._deviceInfo.specs.imaging.ir_resolution_height_px, :, :]
            thermalData = parsedFrame[self._deviceInfo.specs.imaging.ir_resolution_height_px:self._deviceInfo.specs.imaging.ir_resolution_height_px * 2, :, :]
            return imageData, thermalData

        if parsedFrame.ndim == 3 and parsedFrame.shape[0] >= 2:
            imageData, thermalData = np.array_split(parsedFrame, 2, axis=0)
            return imageData, thermalData

        if logWarnings and not self._didLogFrameLayoutWarning:
            self.logger.warning(f"Unsupported frame layout from OpenCV: shape={parsedFrame.shape}, dtype={parsedFrame.dtype}")
            self._didLogFrameLayoutWarning = True

        return None, None

    def _configureCapture(self, cap: cv2.VideoCapture) -> None:
        """Apply capture properties required to preserve thermal bytes."""
        self.logger.info(f"Configuring video capture with backend {self._captureBackend} to preserve thermal data")

        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUY2'))
        # Keep raw bytes; many platforms treat any non-zero as True.
        cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._deviceInfo.specs.imaging.ir_resolution_width_px)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._deviceInfo.specs.imaging.ir_resolution_height_px * 2)
        cap.set(cv2.CAP_PROP_FPS, self._deviceInfo.specs.imaging.frame_rate_hz)

    def _openCapture(self) -> cv2.VideoCapture:
        """
        Opens the video capture and verifies we can read raw (2-channel) frames.

        On Windows especially, some backends ignore CAP_PROP_CONVERT_RGB and return 3-channel BGR,
        which destroys the thermal data. We probe a few backends and only accept one that yields
        a splittable frame with a 2-channel layout.
        """
        self.logger.info("Opening video capture and searching for a backend that provides raw thermal data frames")

        backends: list[int]
        if sys.platform.startswith("win"):
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        elif self._env.isPi:
            # Prefer V4L2 on Pi/Linux to preserve raw YUY2 bytes.
            backends = [cv2.CAP_V4L2, cv2.CAP_ANY]
        else:
            backends = [cv2.CAP_V4L2, cv2.CAP_ANY]

        lastOpenedCap: cv2.VideoCapture | None = None
        lastBackend: int | None = None

        for backend in backends:
            if self._env.isPi:
                # On the Pi, we have to use the V4L2 backend to get raw frames
                cap = cv2.VideoCapture(f"/dev/video{self._deviceIndex}", backend)
            else:
                cap = cv2.VideoCapture(self._deviceIndex, backend)
            if cap is None or not cap.isOpened():
                continue

            lastOpenedCap = cap
            lastBackend = backend

            self._configureCapture(cap)

            # Prime the capture and validate the layout.
            ok = False
            for attempt in range(5):
                ret, frame = cap.read()
                if not ret:
                    self.logger.debug(f"Backend {backend} attempt {attempt}: failed to read frame")
                    continue
                self.logger.debug(f"Backend {backend} attempt {attempt}: frame shape={frame.shape}, dtype={frame.dtype}")
                imdata, thdata = self._splitFrameData(frame, logWarnings=False)
                if imdata is not None and thdata is not None and thdata.ndim == 3 and thdata.shape[2] == 2:
                    self.logger.debug(f"Backend {backend} SUCCESS: thermal data shape={thdata.shape}")
                    ok = True
                    break

            if ok:
                self._captureBackend = backend
                return cap

            cap.release()

        # If we got here, nothing produced a usable raw frame.
        if lastOpenedCap is not None:
            lastOpenedCap.release()
        raise RuntimeError(
            f"Opened device index {self._deviceIndex} but could not obtain a raw YUY2 frame (2-channel). "
            f"Tried backends: {backends}. "
            "This usually means OpenCV is converting to BGR/MJPG, which breaks thermal temperature decoding."
        )

    def run(self):
        """
        Runs the main runtime loop for the program.
        """
        self.logger.info("Beginning ThermalCameraController run.")
        
        # Initialize video
        self._cap = self._openCapture()
        if self._cap is None or not self._cap.isOpened():
            self.logger.critical(f"Failed to open video capture on device index {self._deviceIndex}. No backends produced a usable raw frame.")
            raise RuntimeError(f"Failed to open video device index {self._deviceIndex}")
        # Ensure our settings are applied even if the backend changes behavior after opening.
        self._configureCapture(self._cap)

        # Start main runtime loop
        self.logger.info("Starting main runtime loop")
        while(self._cap.isOpened()):
            ret, frame = self._cap.read()
            if ret == True:
                # Split frame into two parts: image data and thermal data
                imdata, thdata = self._splitFrameData(frame)
                if imdata is None or thdata is None or thdata.size == 0:
                    if not self._didLogFrameLayoutWarning:
                        self.logger.warning(
                            "Failed to split frame data into image and thermal components. "
                            f"Frame shape: {frame.shape}, imdata shape: {imdata.shape if imdata is not None else 'None'}, "
                            f"thdata shape: {thdata.shape if thdata is not None else 'None'}")
                        self._didLogFrameLayoutWarning = True
                    continue

                # Determine which data to use for temperature calculations
                # If swapped, the thermal data is in what we're calling 'imdata'
                temp_data = imdata if self._guiController.showRawThermalData else thdata
                
                # Find the average temperature in the frame
                self._avgTemp = self.calculateAverageTemperature(temp_data)
                self._rawTemp = self.calculateRawTemperature(temp_data) # also updates byte order detection
                self._temp = self.calculateTemperature(temp_data)
                self._minTemp = self.calculateMinimumTemperature(temp_data)
                self._maxTemp = self.calculateMaximumTemperature(temp_data)

                displayTemp = convertTemperatureForDisplay(self._temp, self._temperatureUnit)
                displayMinTemp = convertTemperatureForDisplay(self._minTemp, self._temperatureUnit)
                displayMaxTemp = convertTemperatureForDisplay(self._maxTemp, self._temperatureUnit)
                displayAvgTemp = convertTemperatureForDisplay(self._avgTemp, self._temperatureUnit)
                displayThreshold = convertTemperatureDeltaForDisplay(self._guiController.threshold, self._temperatureUnit)

                # Draw GUI elements
                heatmap = self._guiController.drawGUI(
                    imdata=imdata,
                    thdata=thdata,
                    temp=displayTemp,
                    maxTemp=displayMaxTemp,
                    minTemp=displayMinTemp,
                    averageTemp=displayAvgTemp,
                    labelThreshold=displayThreshold,
                    isRecording=self._isRecording,
                    mcol=self._mcol,
                    mrow=self._mrow,
                    lcol=self._lcol,
                    lrow=self._lrow)

                # Check for recording
                if self._isRecording == True:
                    self._videoOut.write(heatmap)
                    
                # Check for quit and other inputs
                keyPress = cv2.waitKey(KEY_PRESS_DELAY) & 0xFF
                if keyPress == ord(KEY_QUIT):
                    # Check for recording and close out
                    self.logger.info("Quit key pressed. Exiting main loop.")
                    if self._isRecording == True:
                        self._videoOut.release()
                    return

                self._checkForKeyPress(keyPress=keyPress, img=heatmap)
                
                # Display image
                cv2.imshow(self._guiController.windowTitle, heatmap)
