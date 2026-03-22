# PyThermalCamera - Windows

This is a fork of the now-outdated (June 2023) Python script to display the temperature details of the [TopDon TC001 thermal camera](https://www.topdon.com/products/tc001) and similar cameras. See [my EEVGBlog post](https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/msg5787923/#msg5787923).

## Table of Contents

- [Introduction](#introduction)
  - [Why](#why)
  - [Credits](#credits)
- [Features](#features)
  - [Tested Platforms](#tested-platforms)
- [Running and setup](#running-and-setup)
  - [Pre-Flight Checks](#pre-flight-checks)
  - [Running the Program](#running-the-program)
  - [Running Tests](#running-tests)
- [Using the Program](#using-the-program)
  - [Key Bindings](#key-bindings)
- [TODO](#todo)

## Introduction

No commands are sent to the camera. Instead, we take the raw video feed, do some OpenCV processing, and display a nice heatmap along with relevant temperature points highlighted.

I am currently in the process of reverse engineering the commands sent to the camera through USB.

![Screenshot](media/TC00120230701-131032.png)

### Why?

Due to updates to OpenCV, NumPy, and Python, the original script breaks on Windows. I am testing using a [TS001](https://www.topdon.com/products/ts001) on Windows, so this fork is tailored majorly towards that.

I have attempted to flesh out/refactor the program and finish what Les Wright started, making it compatable with Windows systems as well as applying more polished coding practices (proper documentation, no hard-coding, strong-typing, OOP practices, etc.). It started small, but has turned into a full rewrite.

### Credits

The majority of the thermal data configuration work was done by the original repo author (Les Wright) and through the help of others online like LeoDJ. If you'd like to support to Les, you can [donate via this PayPal link](https://paypal.me/leslaboratory?locale.x=en_GB) or [see his YouTube channel](https://www.youtube.com/leslaboratory) and his [video on the TC001](https://youtu.be/PiVwZoQ8_jQ).

LeoDJ was responsible for reverse engineering the image format for these types of cameras (InfiRay P2 Pro). If possible, you should read the [EEVBlog post/thread](https://www.eevblog.com/forum/thermal-imaging/infiray-and-their-p2-pro-discussion/200/) and check out [Leo's GitHub repo](https://github.com/LeoDJ/P2Pro-Viewer).

## Features

Tested on Windows 11 Pro (update 23H2).

> NOTE: Seemingly there are bugs in the compiled version of OpenCV that ships with the Pi, so workarounds have been implemented.

The following features have been implemented:

<img align="right" src="media/colormaps.png" alt="The colormaps supported">

- Temperature reading from device
  - Average Scene Temperature.
  - Center of scene temperature monitoring (crosshair).
  - Floating Maximum and Minimum temperature values within the scene, with variable threshold.
- Temperature unit conversions
- Data-driven device configuration
  - Pre-configured JSON files for common devices, including:
    - TC001
    - TS001
- Data capture
  - Video recording is implemented (saved as AVI in the working directory).
  - Snapshot images are implemented (saved as PNG in the working directory).
- Full set of colormaps
  - False coloring of the video image. Available colormaps are listed on the right.
  - Colors can also be inverted, essentially doubling the amount of colormaps!
- Post-processing options
  - Scaling
    - Bicubic interpolation to scale the small 256*192 image to something more presentable! Available scaling multiplier range from 1-5.
    - Note: This will not auto change the window size on the Pi (OpenCV needs recompiling), however you can manually resize.
  - Blur
  - Contrast
- Fullscreen/windowed modes
  - Note: going back to windowed from fullscreen does not seem to work on the Pi! OpenCV probably needs recompiling.
- Detailed logging system
- Full CLI help pages
- Additional debug features
  - Reversing the image data
  - A Picture-in-Picture (PiP) mode for previewing raw thermal data with image data

### Tested Platforms

#### Operating Systems

- Windows 11
- Raspbian Trixie
- Raspbian Bookworm

#### Hardware/Arch

- x64
- Raspberry Pi 5
- Raspberry Pi 4b

## Running and Setup

### Pre-Flight Checks

> 🛑**MAJOR NOTE**🛑: If you have previously installed the official drivers/application from Topdon's website, ***UNINSTALL THEM COMPLETELY***. If you do not, your system will no longer recognize your camera as UVC-compatible.

Before running the program, please check that you have the following:

- You have connected your camera to your system properly
- You have the correct drivers installed (or just that the camera shows up as a video device)
- You have Python in your `PATH`

If that is in order, the following commands can be used to initialize your environment for multiple platforms:

Linux:

```bash
cd $REPO_ROOT
python -m venv .venv
source ./.venv/bin/activate
```

Windows (CMD):

```bash
cd %REPO_ROOT%
python -m venv .venv
.venv\Scripts\activate.bat
```

Windows (Powershell):

```bash
cd $env:REPO_ROOT
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Then, to install all dependencies inside your virtual environment:

```bash
python -m pip install -r REQUIREMENTS.txt
```

### Running the Program

Generally to run the program, all you need to run is the following:

```bash
python main.py device $DEVICE_CONFIG_JSON -i $VIDEO_INDEX
```

Where:

- `DEVICE_CONFIG_JSON` is the path to the configuration json (i.e. `devices/TC001.json`, `devices/TS001.json`, etc.)
- `VIDEO_INDEX` is the video index for the thermal camera device (i.e. 0 for `/dev/video0`, 1 for `/dev/video1`, etc.).
  - This is based on OpenCV's implementation. It's easier on Linux systems when you can use `v4l2`.

There are also optional flags/arguments that you can pass to help you choose different devices or models. To see them all and details, run the program with the `--help` flag.

### Running Tests

<!-- TODO: add -->
Tests are coming soon. Currently, they are hit or miss.

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
- u : Toggle Celsius/Fahrenheit
- o : Toggle output mode (image data vs temperature data)
- u : Cycle temperature unit
- b : Toggle PiP raw data view
- q : Quit the program

## TODO

- Error checking
- Threading, especially on low speed (but multicore) architectures like the Pi!
- Add graphing
- Ability to arbitrarily measure points.
