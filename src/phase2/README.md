# `equipment.py`

## Overview

The `equipment.py` script is designed to facilitate equipment testing **prior to the experiments**, ensuring that necessary hardware (buttons) and software dependencies are correctly set up and functioning. It supports both Raspberry Pi (RPi) devices for actual hardware interaction and non-RPi devices (e.g. MacBook) for development and testing purposes through simulated button presses using keys on a keyboard.

## Purpose

- For Raspberry Pi (RPi): It configures GPIO pins to listen for button presses on physical buttons connected to the RPi. It also checks for the installation of necessary non-Python software dependencies (`espeak` and `ffmpeg` to support the text to speech functionality).
- For non-RPi Devices: It simulates button presses using keyboard keys ('g' for green, 'b' for blue, 'r' for red), allowing testing of the software without needing the actual RPi hardware setup (during development). Note that it still performs checks for software dependencies.

## How the Check Works

1. Dependency Check: It first checks if all required non-Python software dependencies (`espeak` and `ffmpeg`) are installed. If any are missing, it reports an error and exits the test.
2. Button Press Detection:
- RPi: it listens for physical button presses.
- non-RPi devices: it listens for specific keyboard keys to simulate button presses.
3. Progress Bar: During the test, a progress bar is displayed, indicating the time left to press each button/key during the test (default is 10 seconds).
4. Test Outcome: The test is considered successful only if all three buttons/keys (green, blue, red) are pressed within the given timeout period. It reports success or failure accordingly.

## How to Run

- On Raspberry Pi:
    - Ensure Python is installed.
    - Connect the physical buttons to the specified GPIO pins.
    - Run the script. It will use the physical buttons for the test.
- non-RPi Devices:
    - Ensure Python and the rich library are installed (pip install rich).
    - Run the script in test mode. It will listen for 'g', 'b', and 'r' key presses to simulate button presses.

To successfully run the `equipment.py` script for equipment testing on both Raspberry Pi (RPi) and non-RPi devices, you'll need to install certain Python and non-Python dependencies as below.

## Python Dependencies

`pynput`: This library is used to monitor and control input devices. It is used in the script to simulate button presses on non-RPi devices using keyboard keys.
`rich`: A library for rich text and beautiful formatting in the terminal. The script uses rich to display messages, progress bars, and colour-coded output.

To install these Python dependencies, you can use pip, the Python package installer. Run the following command:
`pip install pynput rich`

## Non-Python Dependencies

`espeak`: A compact, open-source software speech synthesiser for English and other languages. It is used for text-to-speech functionality in the script.
`ffmpeg`: A complete, cross-platform solution to record, convert, and stream audio and video. It is required for handling multimedia content (in this instance audio).

## Installation on Raspberry Pi (RPi)

On an RPi, you might primarily be concerned with the Python dependencies if you're using physical buttons. However, if your project also requires `espeak` and `ffmpeg` for text-to-speech functionality or multimedia processing, you'll need to install those as well.

You can install them using the package manager with the following commands:
`sudo apt-get install espeak ffmpeg`

## Installation on Non-RPi Devices

On non-RPi devices, e.g. MacBook for development and testing, you'll need the same set of dependencies. The Python libraries (`pynput` and `rich`) are installed the same way using `pip` (or equivalent Python package manager). For the non-Python dependencies (`espeak` and `ffmpeg`), the installation process might vary depending on your operating system.

On macOS, you can use Homebrew to install them: i.e. `brew install espeak ffmpeg`.
On Windows, `ffmpeg` can be downloaded from its official website and added to the system PATH. `espeak` can be installed similarly, but it might require additional steps or alternative text-to-speech solutions due to compatibility issues.

## Running the Script

Ensure all the required Python and non-Python dependencies are installed before running the `equipment.py` script.

To run the script, you use the Python interpreter from the command line. Navigate to the directory containing `equipment.py` and run:
```
python equipment.py
```

*Note that this script is a tool for developers/testers to ensure that the setup (both hardware and software) is correctly configured before deploying or using the software in a production environment. It automates the process of checking dependencies and verifying that input methods (buttons) are operational.*
