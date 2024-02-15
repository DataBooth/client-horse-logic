import subprocess
from pynput.keyboard import Key, Listener
import time


class HardwareTester:
    """The HardwareTester class is designed to facilitate hardware testing
    on a Raspberry Pi (RPi) or simulate the same environment on other
    systems for development and testing purposes.
    It checks for necessary software dependencies, sets up real or
    virtual buttons depending on the running environment, and allows for
    the registration of callbacks to handle button presses."""

    def __init__(self, test_mode=False):
        self.is_rpi = self.check_if_rpi()
        self.test_mode = test_mode or not self.is_rpi
        self.button_press_callbacks = {"green": None, "blue": None, "red": None}

        if self.is_rpi and not self.test_mode:
            self.setup_real_buttons()
        else:
            self.start_keyboard_listener()
        # Dependencies with their respective installation commands
        self.dependencies = {
            "espeak": "sudo apt-get install espeak",
            "ffmpeg": "sudo apt-get install ffmpeg",
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

    def setup_real_buttons(self):
        """Configures GPIO pins on the RPi for button inputs,
        setting them up with pull-up resistors and registering
        event detection for button presses."""
        GPIO.setmode(GPIO.BCM)
        # Define GPIO pins for the buttons
        self.button_pins = {"green": 6, "blue": 7, "red": 12}

        # Setup GPIO pins as input with pull-up resistors
        for color, pin in self.button_pins.items():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.real_button_pressed, bouncetime=200)

    def real_button_pressed(self, channel):
        """Callback function for real button presses, determining which button
        was pressed and invoking the registered callback for that button."""
        # Determine which button was pressed based on the channel and call the registered callback
        for color, pin in self.button_pins.items():
            if channel == pin:
                callback = self.button_press_callbacks.get(color)
                if callback:
                    callback()

    def start_keyboard_listener(self):
        """Starts a keyboard listener using the pynput package to simulate
        button presses on systems not running on an RPi.
        Maps specific keys (F1, F2, F3) to virtual buttons."""

        def on_press(key):
            if key == Key.f1:
                if self.button_press_callbacks["green"]:
                    self.button_press_callbacks["green"]()
            elif key == Key.f2:
                if self.button_press_callbacks["blue"]:
                    self.button_press_callbacks["blue"]()
            elif key == Key.f3:
                if self.button_press_callbacks["red"]:
                    self.button_press_callbacks["red"]()

        listener = Listener(on_press=on_press)
        listener.start()

    def register_button_callback(self, button_color, callback):
        """Allows other parts of the code to register callback functions
        for specific button colors (green, blue, red).
        These callbacks are called when the corresponding button is pressed."""
        if button_color in self.button_press_callbacks:
            self.button_press_callbacks[button_color] = callback

    def check_dependency(self):
        """Checks if specified command-line dependencies are installed,
        printing instructions for installation if any are missing."""
        for command, install_command in self.dependencies.items():
            try:
                subprocess.run(
                    [command, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                print(f"{command} is installed.")
            except subprocess.CalledProcessError:
                print(f"{command} is not installed. Please install it using: '{install_command}'")

    def test_hardware(self):
        """Test the hardware setup, including button press detection."""
        print("Testing hardware setup...")
        self.check_dependency()

        if self.is_rpi and not self.test_mode:
            print(
                "Running on Raspberry Pi with real buttons. Press each button to test. Waiting for button presses..."
            )
        else:
            print("Running in TEST mode. Use the keyboard to simulate button presses:")
            print("  - Press F1 for the 'green' button")
            print("  - Press F2 for the 'blue' button")
            print("  - Press F3 for the 'red' button")

        # Temporarily override callbacks for testing
        original_callbacks = self.button_press_callbacks.copy()
        for color in self.button_press_callbacks.keys():
            self.button_press_callbacks[color] = lambda color=color: print(
                f"{color.capitalize()} button detected!"
            )

        print("Testing buttons for 10 seconds. Press the buttons now...")
        time.sleep(10)  # Adjust time as needed for testing

        # Restore original callbacks
        self.button_press_callbacks = original_callbacks


if __name__ == "__main__":
    tester = HardwareTester()
    tester.test_hardware()
