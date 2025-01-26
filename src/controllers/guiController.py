import time
import cv2

from defaults.values import *
from enums.ColormapEnum import Colormap

class GuiController:
    def __init__(self, 
                 windowTitle: str = WINDOW_TITLE, 
                 width: int = SENSOR_WIDTH, 
                 height: int = SENSOR_HEIGHT, 
                 scale: int = SCALE, 
                 colormap: Colormap = COLORMAP, 
                 contrast: float = CONTRAST, 
                 blurRadius: int = BLUR_RADIUS, 
                 threshold: int = THRESHOLD):
        # Passed parameters
        self.windowTitle = windowTitle
        self.width = width
        self.height = height
        self.scale = scale
        self.colormap = colormap
        self.contrast = contrast
        self.blurRadius = blurRadius
        self.threshold = threshold
        
        # Calculated properties
        self.scaledWidth = int(self.width*self.scale)
        self.scaledHeight = int(self.height*self.scale)
        
        # States
        self.isHudVisible: bool = HUD_VISIBLE
        self.isFullscreen: bool = FULLSCREEN
        self.isInverted: bool = False
        
        # Recording stats
        self.recordingStartTime: float = RECORDING_START_TIME
        self.last_snapshot_time: str = LAST_SNAPSHOT_TIME
        self.recordingDuration: str = RECORDING_DURATION
        
        # Other
        self._font = FONT
        
        # Initialize the GUI
        cv2.namedWindow(self.windowTitle, cv2.WINDOW_GUI_NORMAL)
        cv2.resizeWindow(self.windowTitle, self.scaledWidth, self.scaledHeight)
        
    def updateRecordingStats(self):
        """
        Updates the recording stats.
        """
        self.recordingDuration = (time.time() - self.recordingStartTime)
        self.recordingDuration = time.strftime("%H:%M:%S", time.gmtime(self.recordingDuration)) 
        
    def drawGUI(self, imdata, temp, averageTemp, maxTemp, minTemp, isRecording, mrow, mcol, lrow, lcol):
        """
        Draws the GUI elements on the thermal image.
        """
        # Apply affects
        img = self.applyEffects(imdata=imdata)
        
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
            img = self.drawHUD(img, averageTemp, isRecording)
        
        # Display floating max temp
        if maxTemp > averageTemp + self.threshold:
            img = self.drawMaxTemp(img, mrow, mcol, maxTemp)

        # Display floating min temp
        if minTemp < averageTemp - self.threshold:
            img = self.drawMinTemp(img, lrow, lcol, minTemp)
            
        # Update recording stats
        if isRecording == True:
            self.updateRecordingStats()

        return img

    def drawTemp(self, img, temp):
        """
        Draws the temperature onto the image.
        """
        cv2.putText(
            img,
            str(temp)+' C',
            (int(self.scaledWidth/2)+10, int(self.scaledHeight/2)-10),
            self._font,
            0.45,
            (0, 0, 0),
            2,
            cv2.LINE_AA)
        cv2.putText(
            img,
            str(temp)+' C',
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

    def drawHUD(self, img, averageTemp, isRecording):
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
            'Avg Temp: '+str(averageTemp)+' C',
            (10, 14),
            self._font,
            0.4,
            (0, 255, 255),
            1,
            cv2.LINE_AA)

        cv2.putText(
            img,
            'Label Threshold: '+str(self.threshold)+' C',
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
            text=str(maxTemp)+' C', 
            org=((row*self.scale)+10, (col*self.scale)+5),
            fontFace=self._font, 
            fontScale=0.45,
            color=(0,0,0), 
            thickness=2, 
            lineType=cv2.LINE_AA)
        
        cv2.putText(
            img=img,
            text=str(maxTemp)+' C',
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
            str(minTemp)+' C',
            ((row*self.scale)+10,
             (col*self.scale)+5),
            self._font,
            0.45,
            (0,0,0),
            2,
            cv2.LINE_AA)
        cv2.putText(
            img,
            str(minTemp)+' C', 
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
        # Contrast
        img = cv2.convertScaleAbs(imdata, alpha=self.contrast)
        
        # Bicubic interpolate, upscale and blur
        img = cv2.resize(img, (self.scaledWidth,self.scaledHeight), interpolation=cv2.INTER_CUBIC) # Scale up!
        
        # Blur
        if self.blurRadius > 0:
            img = cv2.blur(img,(self.blurRadius, self.blurRadius))

        return img