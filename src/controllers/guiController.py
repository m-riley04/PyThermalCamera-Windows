import time, cv2, logging, numpy as np

from src.defaults.keybinds import *
from src.enums.TemperatureUnitEnum import TemperatureUnit, getSymbolFromTempUnit
from src.models.deviceinfo import DeviceInfo
from src.defaults.values import *
from src.enums.ColormapEnum import Colormap

class GuiController:
    def __init__(self
                 , logger: logging.Logger
                 , windowTitle: str = WINDOW_TITLE
                 , width: int = DEFAULT_SENSOR_WIDTH_PX
                 , height: int = DEFAULT_SENSOR_HEIGHT_PX
                 , scale: int = DEFAULT_SCALE
                 , colormap: Colormap = DEFAULT_COLORMAP
                 , contrast: float = DEFAULT_CONTRAST
                 , blurRadius: int = DEFAULT_BLUR_RADIUS
                 , threshold: int = DEFAULT_THRESHOLD
                 , temperatureUnit: TemperatureUnit = DEFAULT_TEMPERATURE_UNIT
                 , temperatureUnitSymbol: str = DEFAULT_TEMPERATURE_UNIT_SYMBOL
                 , reverseOutput: bool = False):
        self.logger = logger
        self.logger.info("Initializing GUIController.")

        # Passed parameters
        self.windowTitle = windowTitle
        self.width = width
        self.height = height
        self.scale = scale
        self.colormap = colormap
        self.contrast = contrast
        self.blurRadius = blurRadius
        self.threshold = threshold
        self.temperatureUnitSymbol = temperatureUnitSymbol
        self._temperatureUnit = temperatureUnit
        self.reverseOutput = reverseOutput

        # Calculated properties
        self.scaledWidth = int(self.width*self.scale)
        self.scaledHeight = int(self.height*self.scale)
        
        # States
        self.isHudVisible: bool = DEFAULT_HUD_VISIBLE
        self.isFullscreen: bool = DEFAULT_FULLSCREEN
        self.isInverted: bool = False
        self.showPiP: bool = True
        
        # Recording stats
        self.recordingStartTime: float = DEFAULT_RECORDING_START_TIME
        self.last_snapshot_time: str = DEFAULT_LAST_SNAPSHOT_TIME
        self.recordingDuration: str = DEFAULT_RECORDING_DURATION
        
        # Other
        self._font = DEFAULT_FONT
        
        # Initialize the GUI
        cv2.namedWindow(self.windowTitle, cv2.WINDOW_GUI_NORMAL)
        cv2.resizeWindow(self.windowTitle, self.scaledWidth, self.scaledHeight)

        self.logger.info("GUIController initialized with window title: %s, width: %d, height: %d, scale: %d, colormap: %s, contrast: %.1f, blur radius: %d, threshold: %d, temperature unit symbol: %s",
                         self.windowTitle, self.width, self.height, self.scale, self.colormap.name, self.contrast, self.blurRadius, self.threshold, self.temperatureUnitSymbol)
        
    def updateRecordingStats(self):
        """
        Updates the recording stats.
        """
        self.recordingDuration = (time.time() - self.recordingStartTime)
        self.recordingDuration = time.strftime("%H:%M:%S", time.gmtime(self.recordingDuration)) 

    def handleKeyPresses(self, keyPress: int, deviceInfo: DeviceInfo):
        ### BLUR RADIUS
        if keyPress == ord(KEY_INCREASE_BLUR): # Increase blur radius
            self.blurRadius += BLUR_RADIUS_INCREMENT
            self.logger.info("Blur radius increased. New value: %d", self.blurRadius)
        if keyPress == ord(KEY_DECREASE_BLUR): # Decrease blur radius
            self.blurRadius -= BLUR_RADIUS_INCREMENT
            if self.blurRadius <= BLUR_RADIUS_MIN:
                self.blurRadius = BLUR_RADIUS_MIN
            
            self.logger.info("Blur radius decreased. New value: %d", self.blurRadius)

        ### THRESHOLD CONTROL
        if keyPress == ord(KEY_INCREASE_FLOATING_HIGH_LOW_TEMP_LABEL_THRESHOLD): # Increase threshold
            self.threshold += THRESHOLD_INCREMENT
            self.logger.info("Label threshold increased. New value: %d", self.threshold)
        if keyPress == ord(KEY_DECREASE_FLOATING_HIGH_LOW_TEMP_LABEL_THRESHOLD): # Decrease threshold
            self.threshold -= THRESHOLD_INCREMENT
            if self.threshold <= THRESHOLD_MIN:
                self.threshold = THRESHOLD_MIN

            self.logger.info("Label threshold decreased. New value: %d", self.threshold)

        ### SCALE CONTROLS
        if keyPress == ord(KEY_INCREASE_SCALE): # Increase scale
            self.scale += SCALE_INCREMENT
            if self.scale >= SCALE_MAX:
                self.scale = SCALE_MAX
            self.scaledWidth = deviceInfo.specs.imaging.ir_resolution_width_px*self.scale
            self.scaledHeight = deviceInfo.specs.imaging.ir_resolution_height_px*self.scale
            if self.isFullscreen == False:
                cv2.resizeWindow(self.windowTitle, self.scaledWidth, self.scaledHeight)

            self.logger.info("Scale increased. New value: %d", self.scale)
        if keyPress == ord(KEY_DECREASE_SCALE): # Decrease scale
            self.scale -= SCALE_INCREMENT
            if self.scale <= SCALE_MIN:
                self.scale = SCALE_MIN
            self.scaledWidth = deviceInfo.specs.imaging.ir_resolution_width_px*self.scale
            self.scaledHeight = deviceInfo.specs.imaging.ir_resolution_height_px*self.scale
            if self.isFullscreen == False:
                cv2.resizeWindow(self.windowTitle, self.scaledWidth,self.scaledHeight)

            self.logger.info("Scale decreased. New value: %d", self.scale)

        ### FULLSCREEN CONTROLS
        if keyPress == ord(KEY_FULLSCREEN): # Enable fullscreen
            self.isFullscreen = DEFAULT_FULLSCREEN
            cv2.namedWindow(self.windowTitle, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(self.windowTitle, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            
            self.logger.info("Fullscreen mode enabled.")
        if keyPress == ord(KEY_WINDOWED): # Disable fullscreen
            self.isFullscreen = not DEFAULT_FULLSCREEN
            cv2.namedWindow(self.windowTitle, cv2.WINDOW_GUI_NORMAL)
            cv2.setWindowProperty(self.windowTitle, cv2.WND_PROP_AUTOSIZE, cv2.WINDOW_GUI_NORMAL)
            cv2.resizeWindow(self.windowTitle, self.scaledWidth, self.scaledHeight)

            self.logger.info("Windowed mode enabled.")

        ### CONTRAST CONTROLS
        if keyPress == ord(KEY_INCREASE_CONTRAST): # Increase contrast
            self.contrast += CONTRAST_INCREMENT
            self.contrast = round(self.contrast, 1) #fix round error
            if self.contrast >= CONTRAST_MAX:
                self.contrast = CONTRAST_MAX

            self.logger.info("Contrast increased. New value: %.1f", self.contrast)
        if keyPress == ord(KEY_DECREASE_CONTRAST): # Decrease contrast
            self.contrast -= CONTRAST_INCREMENT
            self.contrast = round(self.contrast,1)#fix round error
            if self.contrast <= CONTRAST_MIN:
                self.contrast = CONTRAST_MIN
            
            self.logger.info("Contrast decreased. New value: %.1f", self.contrast)

        ### HUD CONTROLS
        if keyPress == ord(KEY_TOGGLE_HUD): # Toggle HUD
            if self.isHudVisible == True:
                self.isHudVisible = not DEFAULT_HUD_VISIBLE
            elif self.isHudVisible == False:
                self.isHudVisible = DEFAULT_HUD_VISIBLE

            self.logger.info("HUD visibility toggled. New state: %s", self.isHudVisible)

        ### COLOR MAPS
        if keyPress == ord(KEY_CYCLE_THROUGH_COLORMAPS): # Cycle through color maps
            if self.colormap.value + 1 > Colormap.INV_RAINBOW.value:
                self.colormap = Colormap.NONE
            else:
                self.colormap = Colormap(self.colormap.value + 1)
            self.logger.info("Colormap changed to %s", self.colormap.name)
        if keyPress == ord(KEY_INVERT): # Cycle through color maps
            self.logger.info("Inverting colors. Previous state: %s", self.isInverted)
            self.isInverted = not self.isInverted
        
        if keyPress == ord(KEY_TOGGLE_OUTPUT_MODE): # Toggle between processed and raw thermal output
            self.logger.info("Toggling output mode. Previous state: %s", self.reverseOutput)
            self.reverseOutput = not self.reverseOutput
        
        if keyPress == ord(KEY_TOGGLE_PIP): # Toggle PiP window visibility
            self.logger.info("Toggling PiP window visibility. Previous state: %s", self.showPiP)
            self.showPiP = not self.showPiP
        
    def drawGUI(self, imdata, thdata, temp, averageTemp, maxTemp, minTemp, labelThreshold, isRecording, mrow, mcol, lrow, lcol):
        """
        Draws the GUI elements on the thermal image.
        """
        # Swap data sources if reverseOutput is enabled
        # This helps if the camera backend is showing the wrong half of the frame
        if self.reverseOutput:
            display_data = thdata
            pip_data = imdata
        else:
            display_data = imdata
            pip_data = thdata
        
        # Apply affects
        img = self.applyEffects(imdata=display_data)
        
        # Apply inversion
        if self.isInverted == True:
            img = cv2.bitwise_not(img)

        # Apply colormap
        img = self.applyColormap(img)

        # Draw crosshairs
        img = self.drawCrosshairs(img)
        
        # Draw temp
        img = self.drawTemp(img, temp)

        # Draw HUD
        if self.isHudVisible == True:
            img = self.drawHUD(img, averageTemp, labelThreshold, isRecording)
        
        # Display floating max temp
        if maxTemp > averageTemp + labelThreshold:
            img = self.drawMaxTemp(img, mrow, mcol, maxTemp)

        # Display floating min temp
        if minTemp < averageTemp - labelThreshold:
            img = self.drawMinTemp(img, lrow, lcol, minTemp)
            
        # Update recording stats
        if isRecording == True:
            self.updateRecordingStats()
        
        # Show PiP with the alternate data source for comparison if enabled
        if self.showPiP:
            img = self._overlayRawThermalData(img, pip_data, self.reverseOutput)

        return img

    def drawTemp(self, img, temp):
        """
        Draws the temperature onto the image.
        """
        cv2.putText(
            img,
            str(temp)+' '+self.temperatureUnitSymbol,
            (int(self.scaledWidth/2)+10, int(self.scaledHeight/2)-10),
            self._font,
            0.45,
            (0, 0, 0),
            2,
            cv2.LINE_AA)
        cv2.putText(
            img,
            str(temp)+' '+self.temperatureUnitSymbol,
            (int(self.scaledWidth/2)+10, int(self.scaledHeight/2)-10),
            self._font,
            0.45,
            (0, 255, 255),
            1,
            cv2.LINE_AA)
        
        return img

    def drawCrosshairs(self, img):
        """
        Draws crosshairs on the image.
        """
        cv2.line(
            img,
            (int(self.scaledWidth/2),int(self.scaledHeight/2)+20),
            (int(self.scaledWidth/2),int(self.scaledHeight/2)-20),
            (255,255,255),
            2) #vline
        cv2.line(
            img,
            (int(self.scaledWidth/2)+20,int(self.scaledHeight/2)),
            (int(self.scaledWidth/2)-20,int(self.scaledHeight/2)),
            (255,255,255),
            2) #hline

        cv2.line(
            img,
            (int(self.scaledWidth/2),int(self.scaledHeight/2)+20),
            (int(self.scaledWidth/2),int(self.scaledHeight/2)-20),
            (0,0,0),
            1) #vline
        cv2.line(
            img,
            (int(self.scaledWidth/2)+20,int(self.scaledHeight/2)),
            (int(self.scaledWidth/2)-20,int(self.scaledHeight/2)),
            (0,0,0),
            1) #hline
        
        return img

    def drawHUD(self, img, averageTemp, labelThreshold, isRecording):
        """
        Draws the HUD onto the image.
        """
        # Display black box for our data
        cv2.rectangle(
            img, 
            (0, 0),
            (160, 134),
            (0,0,0),
            -1)
        
        # Put text in the box
        cv2.putText(
            img,
            'Avg Temp: '+str(averageTemp)+' '+self.temperatureUnitSymbol,
            (10, 14),
            self._font,
            0.4,
            (0, 255, 255),
            1,
            cv2.LINE_AA)

        cv2.putText(
            img,
            'Label Threshold: '+str(labelThreshold)+' '+self.temperatureUnitSymbol,
            (10, 28),
            self._font,
            0.4,
            (0, 255, 255),
            1,
            cv2.LINE_AA)

        cv2.putText(
            img,
            'Colormap: '+self.colormap.name,
            (10, 42),
            self._font,
            0.4,
            (0, 255, 255),
            1,
            cv2.LINE_AA)

        cv2.putText(
            img,
            'Blur: '+str(self.blurRadius)+' ', 
            (10, 56),
            self._font, 
            0.4,
            (0, 255, 255),
            1,
            cv2.LINE_AA)

        cv2.putText(
            img,
            'Scaling: '+str(self.scale)+' ',
            (10, 70),
            self._font,
            0.4,
            (0, 255, 255),
            1,
            cv2.LINE_AA)

        cv2.putText(
            img,
            'Contrast: '+str(self.contrast)+' ',
            (10, 84),
            self._font,
            0.4,
            (0, 255, 255),
            1,
            cv2.LINE_AA)

        cv2.putText(
            img,
            'Snapshot: '+self.last_snapshot_time+' ',
            (10, 98),
            self._font,
            0.4,
            (0, 255, 255),
            1,
            cv2.LINE_AA)

        if isRecording == False:
            cv2.putText(
                img,
                'Recording: '+str(isRecording),
                (10, 112),
                self._font,
                0.4,
                (200, 200, 200),
                1,
                cv2.LINE_AA)
        else:
            cv2.putText(
                img,
                'Recording: '+self.recordingDuration,
                (10, 112),
                self._font,
                0.4,
                (40, 40, 255),
                1,
                cv2.LINE_AA)
            
        cv2.putText(
            img,
            'Inverted: '+str(self.isInverted),
            (10, 126),
            self._font,
            0.4,
            (0, 255, 255),
            1,
            cv2.LINE_AA)
            
        return img
    
    def drawMaxTemp(self, img, row: int, col: int, maxTemp):
        """
        Draws the maximum temperature point on the image.
        """
        # Draw max temp circle(s)
        cv2.circle(
            img,
            (row*self.scale, col*self.scale),
            5,
            (0,0,0),
            2)
        cv2.circle(
            img,
            (row*self.scale, col*self.scale),
            5,
            (0,0,255),
            -1)
        
        # Draw max temp label(s)
        cv2.putText(
            img=img,
            text=str(maxTemp)+' '+self.temperatureUnitSymbol, 
            org=((row*self.scale)+10, (col*self.scale)+5),
            fontFace=self._font, 
            fontScale=0.45,
            color=(0,0,0), 
            thickness=2, 
            lineType=cv2.LINE_AA)
        
        cv2.putText(
            img=img,
            text=str(maxTemp)+' '+self.temperatureUnitSymbol,
            org=((row*self.scale)+10, (col*self.scale)+5),
            fontFace=self._font,
            fontScale=0.45,
            color=(0, 255, 255),
            thickness=1,
            lineType=cv2.LINE_AA)

        return img
    
    def drawMinTemp(self, img, row: int, col: int, minTemp):
        """
        Draws the minimum temperature point on the image.
        """
        # Draw min temp circle
        cv2.circle(img, (row*self.scale, col*self.scale), 5, (0,0,0), 2)
        cv2.circle(img, (row*self.scale, col*self.scale), 5, (255,0,0), -1)
        
        # Draw min temp label(s)
        cv2.putText(
            img,
            str(minTemp)+' '+self.temperatureUnitSymbol,
            ((row*self.scale)+10,
             (col*self.scale)+5),
            self._font,
            0.45,
            (0,0,0),
            2,
            cv2.LINE_AA)
        cv2.putText(
            img,
            str(minTemp)+' '+self.temperatureUnitSymbol, 
            ((row*self.scale)+10,
             (col*self.scale)+5),
            self._font,
            0.45,
            (0, 255, 255),
            1,
            cv2.LINE_AA)

        return img
    
    def applyColormap(self, img):
        """
        Applies the selected colormap to the image data.
        """
        match Colormap(self.colormap):
            case Colormap.JET:
                img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
            case Colormap.HOT:
                img = cv2.applyColorMap(img, cv2.COLORMAP_HOT)
            case Colormap.MAGMA:
                img = cv2.applyColorMap(img, cv2.COLORMAP_MAGMA)
            case Colormap.INFERNO:
                img = cv2.applyColorMap(img, cv2.COLORMAP_INFERNO)
            case Colormap.PLASMA:
                img = cv2.applyColorMap(img, cv2.COLORMAP_PLASMA)
            case Colormap.BONE:
                img = cv2.applyColorMap(img, cv2.COLORMAP_BONE)
            case Colormap.SPRING:
                img = cv2.applyColorMap(img, cv2.COLORMAP_SPRING)
            case Colormap.AUTUMN:
                img = cv2.applyColorMap(img, cv2.COLORMAP_AUTUMN)
            case Colormap.VIRIDIS:
                img = cv2.applyColorMap(img, cv2.COLORMAP_VIRIDIS)
            case Colormap.PARULA:
                img = cv2.applyColorMap(img, cv2.COLORMAP_PARULA)
            case Colormap.INV_RAINBOW:
                img = cv2.applyColorMap(img, cv2.COLORMAP_RAINBOW)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        return img

    def applyEffects(self, imdata):
        """
        Applies effects (contrast, blur, upscaling, interpolation, etc.) to the image data.
        """
        # Convert thermal camera YUYV image data into BGR for display.
        try:
            imdata = cv2.cvtColor(imdata, cv2.COLOR_YUV2BGR_YUYV)
        except cv2.error:
            pass

        # Contrast
        img = cv2.convertScaleAbs(imdata, alpha=self.contrast)
        
        # Bicubic interpolate, upscale and blur
        img = cv2.resize(img, (self.scaledWidth,self.scaledHeight), interpolation=cv2.INTER_CUBIC) # Scale up!
        
        # Blur
        if self.blurRadius > 0:
            img = cv2.blur(img,(self.blurRadius, self.blurRadius))

        return img
    
    def _overlayRawThermalData(self, img, thdata, is_swapped):
        """
        Overlays the alternate data source as a picture-in-picture window on the main image.
        This shows what the camera is actually sending alongside the processed view.
        When swapped, shows the normal view in PiP while thermal data is the main display.

        TODO: clean this up
        """
        if thdata is None or thdata.size == 0:
            return img
        
        # Calculate PiP window size (roughly 1/3 of the main image)
        pip_width = self.scaledWidth // 3
        pip_height = self.scaledHeight // 3
        
        # Position in bottom-right corner with some padding
        x_offset = self.scaledWidth - pip_width - 10
        y_offset = self.scaledHeight - pip_height - 10
        
        # Try to display as YUY2 (convert from raw bytes)
        try:
            # Treat the 2-channel thermal data as YUYV packed format
            thermal_yuyv = thdata.astype(np.uint8)
            # Convert YUY2 to BGR for display (this will show the raw colors)
            thermal_bgr = cv2.cvtColor(thermal_yuyv, cv2.COLOR_YUV2BGR_YUYV)
        except cv2.error:
            # Fallback: stack the channels to see the raw data
            if thdata.ndim == 2:
                thermal_bgr = cv2.cvtColor(thdata.astype(np.uint8), cv2.COLOR_GRAY2BGR)
            else:
                thermal_bgr = thdata.astype(np.uint8)
                if thermal_bgr.shape[2] == 1:
                    thermal_bgr = cv2.cvtColor(thermal_bgr, cv2.COLOR_GRAY2BGR)
        
        # Resize to PiP dimensions
        pip_img = cv2.resize(thermal_bgr, (pip_width, pip_height), interpolation=cv2.INTER_CUBIC)
        
        # Apply contrast
        pip_img = cv2.convertScaleAbs(pip_img, alpha=self.contrast)
        
        # Draw border around PiP
        cv2.rectangle(img, (x_offset - 2, y_offset - 2), 
                     (x_offset + pip_width + 2, y_offset + pip_height + 2), 
                     (255, 255, 255), 2)
        
        # Label changes based on whether we're swapped or not
        label = 'NORMAL VIEW' if is_swapped else 'THERMAL DATA'
        
        # Add label above PiP
        cv2.putText(
            img,
            label,
            (x_offset, y_offset - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 0, 0),
            2,
            cv2.LINE_AA)
        cv2.putText(
            img,
            label,
            (x_offset, y_offset - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 255, 255),
            1,
            cv2.LINE_AA)
        
        # Overlay the PiP onto the main image
        img[y_offset:y_offset + pip_height, x_offset:x_offset + pip_width] = pip_img
        
        return img