import cv2, time, os, sys
import numpy as np
from numpy.typing import NDArray

from defaults.values import *
from defaults.keybinds import *

from enums.ColormapEnum import Colormap
from controllers.guiController import GuiController
from enums.TemperatureUnitEnum import TemperatureUnit, getSymbolFromTempUnit
from helpers.conversions import convertTemperatureDeltaForDisplay, convertTemperatureForDisplay
from models.deviceinfo import DeviceInfo
from models.envinfo import EnvInfo

class ThermalCameraController:
    def __init__(self, 
                 device: DeviceInfo = DeviceInfo(), 
                 environment: EnvInfo = EnvInfo(),
                 mediaOutputPath: str = DEFAULT_MEDIA_OUTPUT_PATH,
                 temperatureUnit: TemperatureUnit = TemperatureUnit.CELSIUS):
        # Parameters init
        self._deviceInfo: DeviceInfo = device
        self._env: EnvInfo = environment
        self._temperatureUnit: TemperatureUnit = temperatureUnit
        self._temperatureUnitSymbol: str = getSymbolFromTempUnit(self._temperatureUnit)

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
            os.makedirs(self._mediaOutputPath)
        
        # GUI Init
        self._guiController = GuiController(
            width=self._deviceInfo.width,
            height=self._deviceInfo.height,
            temperatureUnitSymbol=self._temperatureUnitSymbol)
        
        # OpenCV init
        self._cap = None
        self._videoOut = None
        self._didLogFrameLayoutWarning = False
        self._captureBackend = None
        self._thermalByteOrder: str | None = None  # "lsb0" (byte0 is LSB) or "lsb1" (byte1 is LSB)
        self._didLogThermalByteOrder = False

    def _rawFromBytes(self, byte0: int, byte1: int) -> int:
        """Combine two uint8 bytes into a 16-bit raw temperature sample.

        The original TC001 script treats channel 0 as the LSB and channel 1 as the MSB.
        Some Windows capture paths/backends can swap this ordering, so we allow autodetection.
        """
        if self._thermalByteOrder == "lsb1":
            return int(byte1) + (int(byte0) << 8)
        return int(byte0) + (int(byte1) << 8)
    
    def is_plausible_celsius(self, temp: float) -> bool:
        """
        Checks if a temperature is within a plausible range for Celsius temperatures that the device should be able to read.
        Used primarily for autodetecting byte order and errors in data.
        """
        return self._deviceInfo.temp_min_c <= temp <= self._deviceInfo.temp_max_c

    def _maybeDetectThermalByteOrder(self, thdata: NDArray) -> None:
        """Detect swapped byte order once using a plausibility check.

        We choose the ordering whose *center pixel* temperature lands in a reasonable range.
        If both are unreasonable (e.g. synthetic test data), we keep the default.
        """

        if self._thermalByteOrder is not None:
            return

        if thdata is None or thdata.size == 0 or thdata.ndim < 3 or thdata.shape[2] < 2:
            self._thermalByteOrder = "lsb0"
            return

        centerRow = thdata.shape[0] // 2
        centerCol = thdata.shape[1] // 2
        b0 = int(thdata[centerRow, centerCol, 0])
        b1 = int(thdata[centerRow, centerCol, 1])

        raw_lsb0 = int(b0) + (int(b1) << 8)
        raw_lsb1 = int(b1) + (int(b0) << 8)
        t0 = float(self.normalizeTemperature(raw_lsb0))
        t1 = float(self.normalizeTemperature(raw_lsb1))

        if self.is_plausible_celsius(t1) and not self.is_plausible_celsius(t0):
            self._thermalByteOrder = "lsb1"
        else:
            self._thermalByteOrder = "lsb0"

        if self._thermalByteOrder == "lsb1" and not self._didLogThermalByteOrder:
            print(
                "Detected swapped thermal byte order (Windows capture). "
                "Using channel0 as MSB / channel1 as LSB for temperature decode."
            )
            self._didLogThermalByteOrder = True

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
        Checks and acts on key presses.
        """
        ### BLUR RADIUS
        if keyPress == ord(KEY_INCREASE_BLUR): # Increase blur radius
            self._guiController.blurRadius += BLUR_RADIUS_INCREMENT
        if keyPress == ord(KEY_DECREASE_BLUR): # Decrease blur radius
            self._guiController.blurRadius -= BLUR_RADIUS_INCREMENT
            if self._guiController.blurRadius <= BLUR_RADIUS_MIN:
                self._guiController.blurRadius = BLUR_RADIUS_MIN

        ### THRESHOLD CONTROL
        if keyPress == ord(KEY_INCREASE_FLOATING_HIGH_LOW_TEMP_LABEL_THRESHOLD): # Increase threshold
            self._guiController.threshold += THRESHOLD_INCREMENT
        if keyPress == ord(KEY_DECREASE_FLOATING_HIGH_LOW_TEMP_LABEL_THRESHOLD): # Decrease threashold
            self._guiController.threshold -= THRESHOLD_INCREMENT
            if self._guiController.threshold <= THRESHOLD_MIN:
                self._guiController.threshold = THRESHOLD_MIN

        ### SCALE CONTROLS
        if keyPress == ord(KEY_INCREASE_SCALE): # Increase scale
            self._guiController.scale += SCALE_INCREMENT
            if self._guiController.scale >= SCALE_MAX:
                self._guiController.scale = SCALE_MAX
            self._guiController.scaledWidth = self._deviceInfo.width*self._guiController.scale
            self._guiController.scaledHeight = self._deviceInfo.height*self._guiController.scale
            if self._guiController.isFullscreen == False:
                cv2.resizeWindow(self._guiController.windowTitle, self._guiController.scaledWidth, self._guiController.scaledHeight)
        if keyPress == ord(KEY_DECREASE_SCALE): # Decrease scale
            self._guiController.scale -= SCALE_INCREMENT
            if self._guiController.scale <= SCALE_MIN:
                self._guiController.scale = SCALE_MIN
            self._guiController.scaledWidth = self._deviceInfo.width*self._guiController.scale
            self._guiController.scaledHeight = self._deviceInfo.height*self._guiController.scale
            if self._guiController.isFullscreen == False:
                cv2.resizeWindow(self._guiController.windowTitle, self._guiController.scaledWidth,self._guiController.scaledHeight)

        ### FULLSCREEN CONTROLS
        if keyPress == ord(KEY_FULLSCREEN): # Enable fullscreen
            self._guiController.isFullscreen = DEFAULT_FULLSCREEN
            cv2.namedWindow(self._guiController.windowTitle, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(self._guiController.windowTitle, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        if keyPress == ord(KEY_WINDOWED): # Disable fullscreen
            self._guiController.isFullscreen = not DEFAULT_FULLSCREEN
            cv2.namedWindow(self._guiController.windowTitle, cv2.WINDOW_GUI_NORMAL)
            cv2.setWindowProperty(self._guiController.windowTitle, cv2.WND_PROP_AUTOSIZE, cv2.WINDOW_GUI_NORMAL)
            cv2.resizeWindow(self._guiController.windowTitle, self._guiController.scaledWidth, self._guiController.scaledHeight)

        ### CONTRAST CONTROLS
        if keyPress == ord(KEY_INCREASE_CONTRAST): # Increase contrast
            self._guiController.contrast += CONTRAST_INCREMENT
            self._guiController.contrast = round(self._guiController.contrast, 1) #fix round error
            if self._guiController.contrast >= CONTRAST_MAX:
                self._guiController.contrast = CONTRAST_MAX
        if keyPress == ord(KEY_DECREASE_CONTRAST): # Decrease contrast
            self._guiController.contrast -= CONTRAST_INCREMENT
            self._guiController.contrast = round(self._guiController.contrast,1)#fix round error
            if self._guiController.contrast <= CONTRAST_MIN:
                self._guiController.contrast = CONTRAST_MIN

        ### HUD CONTROLS
        if keyPress == ord(KEY_TOGGLE_HUD): # Toggle HUD
            if self._guiController.isHudVisible == True:
                self._guiController.isHudVisible = not DEFAULT_HUD_VISIBLE
            elif self._guiController.isHudVisible == False:
                self._guiController.isHudVisible = DEFAULT_HUD_VISIBLE

        if keyPress == ord(KEY_TOGGLE_TEMP_UNIT): # Toggle temperature unit
            if self._temperatureUnit == TemperatureUnit.CELSIUS:
                self._temperatureUnit = TemperatureUnit.FAHRENHEIT
            elif self._temperatureUnit == TemperatureUnit.FAHRENHEIT:
                self._temperatureUnit = TemperatureUnit.KELVIN
            else:
                self._temperatureUnit = TemperatureUnit.CELSIUS

            self._temperatureUnitSymbol = getSymbolFromTempUnit(self._temperatureUnit)
            self._guiController.temperatureUnitSymbol = self._temperatureUnitSymbol

        ### COLOR MAPS
        if keyPress == ord(KEY_CYCLE_THROUGH_COLORMAPS): # Cycle through color maps
            if self._guiController.colormap.value + 1 > Colormap.INV_RAINBOW.value:
                self._guiController.colormap = Colormap.NONE
            else:
                self._guiController.colormap = Colormap(self._guiController.colormap.value + 1)
        if keyPress == ord(KEY_INVERT): # Cycle through color maps
            self._guiController.isInverted = not self._guiController.isInverted
            
        
        ### RECORDING/MEDIA CONTROLS
        if keyPress == ord(KEY_RECORD) and self._isRecording == False: # Start recording
            self._videoOut = self._record()
            self._isRecording = DEFAULT_RECORDING_STATE
            self._guiController.recordingStartTime = time.time()
            
        if keyPress == ord(KEY_STOP): # Stop reording
            self._isRecording = not DEFAULT_RECORDING_STATE
            self._guiController.recordingDuration = DEFAULT_RECORDING_DURATION

        if keyPress == ord(KEY_SNAPSHOT): # Take a snapshot
            self._guiController.last_snapshot_time = self._snapshot(img)

    def _record(self):
        """
        STart recording video to file.
        """
        currentTimeStr = time.strftime("%Y%m%d--%H%M%S")
        #do NOT use mp4 here, it is flakey!
        self._videoOut = cv2.VideoWriter(
            f"{self._mediaOutputPath}/{currentTimeStr}-output.avi",
            cv2.VideoWriter_fourcc(*'XVID'),
            self._deviceInfo.fps,
            (self._guiController.scaledWidth, self._guiController.scaledHeight))
        return self._videoOut
    
    def _snapshot(self, img):
        """
        Takes a snapshot of the current frame.
        """
        #I would put colons in here, but it Win throws a fit if you try and open them!
        currentTimeStr = time.strftime("%Y%m%d-%H%M%S") 
        self._guiController.last_snapshot_time = time.strftime("%H:%M:%S")
        cv2.imwrite(f"{self._mediaOutputPath}/{self._deviceInfo.name}-{currentTimeStr}.png", img)
        return self._guiController.last_snapshot_time

    def normalizeTemperature(self, rawTemp: float, d: int = 64, c: float = 273.15) -> float:
        """
        Normalizes/converts the raw temperature data using the formula found by LeoDJ.
        Link: https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/200/
        """
        return (rawTemp/d) - c

    def calculateTemperature(self, thdata: NDArray) -> float:
        """
        Calculates the (normalized) temperature of the frame.
        """
        raw = self.calculateRawTemperature(thdata)
        return round(self.normalizeTemperature(raw), DEFAULT_TEMPERATURE_SIG_DIGITS)

    def calculateRawTemperature(self, thdata: NDArray) -> float:
        """
        Calculates the raw temperature of the center of the frame.
        """
        if thdata.size == 0 or thdata.shape[0] == 0 or thdata.shape[1] == 0:
            return DEFAULT_TEMPERATURE_RAW

        self._maybeDetectThermalByteOrder(thdata)

        centerRow = thdata.shape[0] // 2
        centerCol = thdata.shape[1] // 2
        b0 = int(thdata[centerRow, centerCol, 0])
        b1 = int(thdata[centerRow, centerCol, 1])
        return self._rawFromBytes(b0, b1)

    def calculateAverageTemperature(self, thdata: NDArray) -> float:
        """
        Calculates the average temperature of the frame.
        """
        if thdata is None or thdata.size == 0 or thdata.ndim < 3 or thdata.shape[2] < 2:
            return DEFAULT_TEMPERATURE_AVG

        self._maybeDetectThermalByteOrder(thdata)
        b0avg = int(thdata[..., 0].mean())
        b1avg = int(thdata[..., 1].mean())
        raw = self._rawFromBytes(b0avg, b1avg)
        return round(self.normalizeTemperature(raw), DEFAULT_TEMPERATURE_SIG_DIGITS)

    def calculateMinimumTemperature(self, thdata: NDArray) -> float:
        """
        Calculates the minimum temperature of the frame.
        """
        # Find the min temperature in the frame
        posmin = int(thdata[...,1].argmin())
        
        # Since argmax returns a linear index, convert back to row and col
        width = thdata.shape[1]
        self._lcol, self._lrow = divmod(posmin, width)
        self._maybeDetectThermalByteOrder(thdata)
        b0 = int(thdata[self._lcol, self._lrow, 0])
        b1 = int(thdata[self._lcol, self._lrow, 1])
        raw = self._rawFromBytes(b0, b1)

        return round(self.normalizeTemperature(raw), DEFAULT_TEMPERATURE_SIG_DIGITS)

    def calculateMaximumTemperature(self, thdata: NDArray) -> float:
        """
        Calculates the maximum temperature of the frame.
        """
        # Find the max temperature in the frame
        lomax = int(thdata[...,1].max())
        posmax = int(thdata[...,1].argmax())

        # Since argmax returns a linear index, convert back to row and col
        width = thdata.shape[1]
        self._mcol, self._mrow = divmod(posmax, width)
        self._maybeDetectThermalByteOrder(thdata)
        b0 = int(thdata[self._mcol, self._mrow, 0])
        b1 = int(thdata[self._mcol, self._mrow, 1])
        raw = self._rawFromBytes(b0, b1)

        return round(self.normalizeTemperature(raw), DEFAULT_TEMPERATURE_SIG_DIGITS)

    def _splitFrameData(self, frame: NDArray, *, logWarnings: bool = True) -> tuple[NDArray | None, NDArray | None]:
        """
        Splits frame into visible-image and thermal-data halves, handling backend-specific layouts.
        """
        if frame is None or frame.size == 0:
            return None, None

        parsedFrame = frame

        # If OpenCV has already converted to BGR/RGB (3 channels) we can no longer recover thermal bytes.
        # Fail fast with a clear warning rather than producing nonsense temperatures.
        if parsedFrame.ndim == 3 and parsedFrame.shape[2] != 2:
            if logWarnings and not self._didLogFrameLayoutWarning:
                print(
                    "OpenCV returned a converted frame (not raw YUY2). "
                    f"shape={parsedFrame.shape}, dtype={parsedFrame.dtype}. "
                    "Thermal bytes are not available; try a different backend (DSHOW vs MSMF) or disable RGB conversion."
                )
                self._didLogFrameLayoutWarning = True
            return None, None

        totalRows = self._deviceInfo.height * 2

        # Some backends return flattened buffers (often with padded row stride).
        if parsedFrame.ndim == 2:
            flattened = parsedFrame.reshape(-1)
            if flattened.size % totalRows == 0:
                bytesPerRow = flattened.size // totalRows
                if bytesPerRow % 2 == 0:
                    pixelsPerRow = bytesPerRow // 2
                    if pixelsPerRow >= self._deviceInfo.width:
                        parsedFrame = flattened.reshape((totalRows, pixelsPerRow, 2))
                        parsedFrame = parsedFrame[:, :self._deviceInfo.width, :]

        if parsedFrame.ndim == 3 and parsedFrame.shape[0] >= totalRows:
            imageData = parsedFrame[:self._deviceInfo.height, :, :]
            thermalData = parsedFrame[self._deviceInfo.height:self._deviceInfo.height * 2, :, :]
            return imageData, thermalData

        if parsedFrame.ndim == 3 and parsedFrame.shape[0] >= 2:
            imageData, thermalData = np.array_split(parsedFrame, 2, axis=0)
            return imageData, thermalData

        if logWarnings and not self._didLogFrameLayoutWarning:
            print(f"Unsupported frame layout from OpenCV: shape={parsedFrame.shape}, dtype={parsedFrame.dtype}")
            self._didLogFrameLayoutWarning = True

        return None, None

    def _configureCapture(self, cap: cv2.VideoCapture) -> None:
        """Apply capture properties required to preserve thermal bytes."""
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUY2'))
        # Keep raw bytes; many platforms treat any non-zero as True.
        cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._deviceInfo.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._deviceInfo.height * 2)
        cap.set(cv2.CAP_PROP_FPS, self._deviceInfo.fps)

    def _openCapture(self) -> cv2.VideoCapture:
        """Opens the video capture and verifies we can read raw (2-channel) frames.

        On Windows especially, some backends ignore CAP_PROP_CONVERT_RGB and return 3-channel BGR,
        which destroys the thermal data. We probe a few backends and only accept one that yields
        a splittable frame with a 2-channel layout.
        """
        backends: list[int]
        if sys.platform.startswith("win"):
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        else:
            backends = [cv2.CAP_ANY] # TODO: maybe do better env checks for linux/pi?

        lastOpenedCap: cv2.VideoCapture | None = None
        lastBackend: int | None = None

        for backend in backends:
            if self._env.isPi:
                # On the Pi, we have to use the V4L2 backend to get raw frames
                cap = cv2.VideoCapture(f"/dev/video{self._deviceInfo.index}", backend)
            else:
                cap = cv2.VideoCapture(self._deviceInfo.index, backend)
            if cap is None or not cap.isOpened():
                continue

            lastOpenedCap = cap
            lastBackend = backend

            self._configureCapture(cap)

            # Prime the capture and validate the layout.
            ok = False
            for _ in range(5):
                ret, frame = cap.read()
                if not ret:
                    continue
                imdata, thdata = self._splitFrameData(frame, logWarnings=False)
                if imdata is not None and thdata is not None and thdata.ndim == 3 and thdata.shape[2] == 2:
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
            f"Opened device index {self._deviceInfo.index} but could not obtain a raw YUY2 frame (2-channel). "
            f"Tried backends: {backends}. "
            "This usually means OpenCV is converting to BGR/MJPG, which breaks thermal temperature decoding."
        )

    def run(self):
        """
        Runs the main runtime loop for the program.
        """
        # Initialize video
        self._cap = self._openCapture()
        if self._cap is None or not self._cap.isOpened():
            raise RuntimeError(f"Failed to open video device index {self._deviceInfo.index}")
        # Ensure our settings are applied even if the backend changes behavior after opening.
        self._configureCapture(self._cap)

        # Start main runtime loop
        while(self._cap.isOpened()):
            ret, frame = self._cap.read()
            if ret == True:
                # Split frame into two parts: image data and thermal data
                imdata, thdata = self._splitFrameData(frame)
                if imdata is None or thdata is None or thdata.size == 0:
                    if not self._didLogFrameLayoutWarning:
                        print(
                            "Failed to split frame data into image and thermal components. "
                            f"Frame shape: {frame.shape}, imdata shape: {imdata.shape if imdata is not None else 'None'}, "
                            f"thdata shape: {thdata.shape if thdata is not None else 'None'}")
                        self._didLogFrameLayoutWarning = True
                    continue

                # Find the average temperature in the frame
                self._avgTemp = self.calculateAverageTemperature(thdata)
                self._rawTemp = self.calculateRawTemperature(thdata) # also updates byte order detection
                self._temp = self.calculateTemperature(thdata)
                self._minTemp = self.calculateMinimumTemperature(thdata)
                self._maxTemp = self.calculateMaximumTemperature(thdata)

                displayTemp = convertTemperatureForDisplay(self._temp, self._temperatureUnit)
                displayMinTemp = convertTemperatureForDisplay(self._minTemp, self._temperatureUnit)
                displayMaxTemp = convertTemperatureForDisplay(self._maxTemp, self._temperatureUnit)
                displayAvgTemp = convertTemperatureForDisplay(self._avgTemp, self._temperatureUnit)
                displayThreshold = convertTemperatureDeltaForDisplay(self._guiController.threshold, self._temperatureUnit)

                # Draw GUI elements
                heatmap = self._guiController.drawGUI(
                    imdata=imdata,
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
                    if self._isRecording == True:
                        self._videoOut.release()
                    return

                self._checkForKeyPress(keyPress=keyPress, img=heatmap)
                
                # Display image
                cv2.imshow(self._guiController.windowTitle, heatmap)
