import subprocess
from pynput.keyboard import Key, Listener
import time


class Equipment:
    """The Equipment class is designed to facilitate equipment testing
    on a Raspberry Pi (RPi) or simulate the same environment on other
    systems for development and testing purposes.
    It checks for necessary non-Python software dependencies, sets up real or
    virtual buttons (keys) depending on the running environment, and allows for
    the registration of callbacks to handle button presses."""

    def __init__(self, test_mode=False):
        self.is_rpi = self.check_if_rpi()
        self.test_mode = test_mode or not self.is_rpi
        self.button_press_callbacks = {"green": None, "blue": None, "red": None}

        if self.is_rpi:
            print("INFO: RasberryPi detected")
        else:
            print("INFO: Running on non-RaspberryPi device")

        if self.is_rpi and not self.test_mode:
            self.setup_buttons()
            print("INFO: Using real buttons")
        else:
            print("INFO: Running in TEST mode")
            print("INFO: Using keys (g - green, b - blue, r - red) to simulate buttons")
            self.start_keyboard_listener()
        # Dependencies with their respective installation commands
        self.dependencies = {
            "espeak": {"install": "sudo apt-get install espeak", "version_cmd": ["espeak", "--version"]},
            "ffmpeg": {"install": "sudo apt-get install ffmpeg", "version_cmd": ["ffmpeg", "-version"]},
        }

    def check_if_rpi(self):
        """Checks if the current system is a Raspberry Pi by attempting
        to read a specific file in the system's firmware directory.
        Returns True if running on an RPi, otherwise False."""
        try:
            with open("/sys/firmware/devicetree/base/model", "r") as f:
                if "Raspberry Pi" in f.read():
                    return True
        except Exception:
            return False

    def setup_buttons(self):
        """Configures GPIO pins on the RPi for button inputs,
        setting them up with pull-up resistors and registering
        event detection for button presses."""
        GPIO.setmode(GPIO.BCM)
        # Define GPIO pins for the buttons
        self.button_pins = {"green": 6, "blue": 7, "red": 12}

        # Setup GPIO pins as input with pull-up resistors
        for colour, pin in self.button_pins.items():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.button_pressed, bouncetime=200)

    def button_pressed(self, channel):
        """Callback function for real button presses, determining which button
        was pressed and invoking the registered callback for that button."""
        # Determine which button was pressed based on the channel and call the registered callback
        for colour, pin in self.button_pins.items():
            if channel == pin:
                callback = self.button_press_callbacks.get(colour)
                if callback:
                    callback()

    def start_keyboard_listener(self):
        """Starts a keyboard listener using the pynput package to simulate
        button presses on systems not running on an RPi.
        Maps specific keys (g - green, b - blue, r - red) to virtual buttons."""

        def on_press(key):
            if str(key) == "'g'":
                if self.button_press_callbacks["green"]:
                    self.button_press_callbacks["green"]()
            elif str(key) == "'b'":
                if self.button_press_callbacks["blue"]:
                    self.button_press_callbacks["blue"]()
            elif str(key) == "'r'":
                if self.button_press_callbacks["red"]:
                    self.button_press_callbacks["red"]()

        listener = Listener(on_press=on_press, suppress=True)
        listener.start()

    def register_button_callback(self, button_colour, callback):
        """Allows other parts of the code to register callback functions
        for specific button colours (green, blue, red).
        These callbacks are called when the corresponding button is pressed."""
        if button_colour in self.button_press_callbacks:
            self.button_press_callbacks[button_colour] = callback

    def check_non_python_dependencies(self):
        """Checks if specified command-line dependencies are installed,
        printing instructions for installation if any are missing.
        Returns False if any dependency is missing, True otherwise."""
        all_dependencies_installed = True
        for command, info in self.dependencies.items():
            try:
                subprocess.run(
                    info["version_cmd"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                print(f"INFO: {command} is installed.")
            except subprocess.CalledProcessError:
                print(f"ERROR: {command} is not installed. Please install it using: '{info['install']}'")
                all_dependencies_installed = False
        return all_dependencies_installed

    def check(self, max_duration_seconds=10):
        """Test the equipment setup, including button press detection.
        Displays a timeout progress bar while waiting for a button/key press."""
        print("\nINFO: Testing equipment setup...")
        print("      - Checking command line (non-Python) dependencies")

        if not self.check_non_python_dependencies():
            print("ERROR: Missing dependencies. Exiting test.")
            return  # Exit the method if dependencies are missing

        # Temporarily override callbacks for testing
        original_callbacks = self.button_press_callbacks.copy()
        button_pressed_flag = False

        def test_callback(colour):
            nonlocal button_pressed_flag
            print(f"\nINFO: {colour.capitalize()} button/key detected!")
            button_pressed_flag = True

        for colour in self.button_press_callbacks.keys():
            button_pressed_flag = False  # Reset flag for each button
            print(f"\nPlease press the {colour} button/key now...")
            print("Progress: ", end="")

            # Override the callback for the current button to provide immediate feedback
            self.button_press_callbacks[colour] = lambda colour=colour: test_callback(colour)

            # Display progress bar
            progress_length = 30  # Length of the progress bar
            start_time = time.time()
            while time.time() - start_time < max_duration_seconds and not button_pressed_flag:
                elapsed_time = time.time() - start_time
                progress = int((elapsed_time / max_duration_seconds) * progress_length)
                print("#" * progress + "-" * (progress_length - progress), end="\r")
                time.sleep(0.1)  # Short sleep to reduce CPU usage while waiting

            if not button_pressed_flag:
                print(f"\nWARNING: No {colour} button/key press detected.")

        # Restore original callbacks
        self.button_press_callbacks = original_callbacks


if __name__ == "__main__":
    equipment = Equipment(test_mode=True)
    equipment.check()
