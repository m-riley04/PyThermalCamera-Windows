# PyThermalCamera - Windows
This is a fork of the now-outdated (June 2023) Python script to display the temperature details of the [TopDon TC001 thermal camera](https://www.topdon.com/products/tc001) and similar cameras. See [my EEVGBlog post](https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/msg5787923/#msg5787923).

## Table of Contents
- [Introduction](#introduction)
    - [Why](#why)
    - [Credits](#credits)
- [Features](#features)
- [Dependencies](#dependencies)
- [Running the Program](#running-the-program)
    - [Basic Sandbox Program](#basic-sandbox-program)
- [Using the Program](#using-the-program)
    - [Key Bindings](#key-bindings)
- [TODO](#todo)

## Introduction
No commands are sent to the camera. Instead, we take the raw video feed, do some OpenCV processing, and display a nice heatmap along with relevant temperature points highlighted.

![Screenshot](media/TC00120230701-131032.png)

### Why?
Due to updates to OpenCV, NumPy, and Python, the original script breaks on Windows. I am testing using a [TS001](https://www.topdon.com/products/ts001) on Windows, so this fork is tailored majorly towards that (but hypothetically could work on Linux and other platforms).

I have attempted to flesh out/refactor the program and finish what Les Wright started, making it compatable with Windows systems as well as applying more polished coding practices (proper documentation, no hard-coding, strong-typing, OOP practices, etc.). It started small, but has turned into practically a full rewrite.

### Credits
The majority of the thermal data configuration work was done by the original repo author (Les Wright) and through the help of others online like LeoDJ. If you'd like to support to Les, you can [donate via this PayPal link](https://paypal.me/leslaboratory?locale.x=en_GB) or [see his YouTube channel](https://www.youtube.com/leslaboratory) and his [video on the TC001](https://youtu.be/PiVwZoQ8_jQ).

LeoDJ was responsible for reverse engineering the image format for these types of cameras (InfiRay P2 Pro). If possible, you should read the [EEVBlog post/thread](https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/200/) and check out [Leo's GitHub repo](https://github.com/LeoDJ/P2Pro-Viewer).

## Features
Tested on Windows 11 Pro (update 23H2). 

> NOTE: Seemingly there are bugs in the compiled version of OpenCV that ships with the Pi. No workarounds have been re-implemented for the Raspberry Pi from the original code due to the workaround actually *breaking* the program on Windows. I'm not sure exactly when it broke, but it must have been between the past 2-3 years.

The following features have been implemented:

<img align="right" src="media/colormaps.png">

- Bicubic interpolation to scale the small 256*192 image to something more presentable! Available scaling multiplier range from 1-5 (Note: This will not auto change the window size on the Pi (openCV needs recompiling), however you can manually resize). Optional blur can be applied if you want to smooth out the pixels. 
- Fullscreen / Windowed mode (Note going back to windowed  from fullscreen does not seem to work on the Pi! OpenCV probably needs recompiling!).
- False coloring of the video image is provided. the avilable colormaps are listed on the right.
- Variable Contrast.
- Average Scene Temperature.
- Center of scene temperature monitoring (Crosshairs).
- Floating Maximum and Minimum temperature values within the scene, with variable threshold.
- Video recording is implemented (saved as AVI in the working directory).
- Snapshot images are implemented (saved as PNG in the working directory).
- Invert the colormap (essentially double the color themes!)

The current settings are displayed in a box at the top left of the screen (The HUD):

- Avg Temperature of the scene
- Label threshold (temperature threshold at which to display floating min max values)
- Colormap
- Blur (blur radius)
- Scaling multiplier
- Contrast value
- Time of the last snapshot image
- Recording status

## Dependencies
- Python (v3.12.4)
- python-opencv (v##.##.##)
- numpy (v##.##.##)

## Running the Program
> **MAJOR NOTE**: If you have previously installed the official drivers/application from Topdon's website, ***UNINSTALL THEM COMPLETELY***. If you do not, your system will no longer recognize your camera as UVC-compatible.

Before running the program, please check that you have the following:
- You have connected your camera to your system properly
- You have the correct drivers installed (or just that the camera shows up as a video device)
- You have all dependencies installed
- You have Python in your `PATH`
- You are starting in the root directory of the repo

If that is in order, the following command can be used to run the program:

```bash
python src/main.py
```

There are also optional flags/arguments that you can pass:
- `--device [device_index]`: specifies the device to use based on it's index

### Basic Sandbox Program
`tc001-RAW.py`: Just demonstrates how to grab raw frames from the Thermal Camera, a starting point if you want to code your own app ***(currently untouched from the fork)***

## Using the Program
### Key Bindings
These keybindings can be changed easily in the `defaults/keybinds.py` file.
- a z: Increase/Decrease Blur
- s x: Floating High and Low Temp Label Threshold'
- d c: Change Interpolated scale.(Note: This will not change the window size on the Pi!)
- f v: Contrast
- e w: Fullscreen Windowed. (Note: Going back to windowed does not seem to work on the Pi!)
- r t: Record and Stop
- m : Cycle through colormaps
- i : Invert the colormap
- h : Toggle HUD
- q : Quit the program

## TODO 
> NOTE: This to-do list will be moved into a public GitHub Kanban soon, but it's 2am and I'm tired.

- Find versions of dependencies 
- Temperature values appear to be calculated incorrectly at the moment. Unsure if it's something I did/removed (since I never got the "original" working)
- Error checking
- Threading, especially on low speed (but multicore) architectures like the Pi!
- Add graphing
- Ability to arbitrarily measure points.
