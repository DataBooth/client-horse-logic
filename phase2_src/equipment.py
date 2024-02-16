import subprocess
import time

from pynput.keyboard import Key, Listener
from rich.console import Console
from text_to_speech import TextToSpeechGoogle

console = Console()  # Create a Rich console object


# import threading
# def tts_test():
#     try:
#         tts_google.speak("Please confirm if you can hear this message by typing 'y'.")
#         user_response = input("Did you hear the spoken message? (y/n): ").strip().lower()
#         if user_response[0] != "y":
#             console.print("[bold red]ERROR:[/bold red] Text-to-speech functionality check failed. User did not confirm hearing the message.")
#     except Exception as e:
#         console.print(f"[bold red]ERROR:[/bold red] Text-to-speech functionality check failed: {e}")

# # Run the TTS test in a separate thread
# tts_thread = threading.Thread(target=tts_test)
# tts_thread.start()

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
            try:
                global GPIO
                import RPi.GPIO as GPIO

                print("[bold]INFO:[/bold] RPi.GPIO module imported successfully.")
            except ImportError:
                print("[bold]ERROR:[/bold] RPi.GPIO module not found. Running in non-RPi mode.")
                self.is_rpi = False  # Ensure is_rpi reflects the availability of RPi.GPIO
        else:
            print("[bold]INFO:[/bold] Not running on Raspberry Pi. Running in non-RPi mode.")

        if self.is_rpi and not self.test_mode:
            self.setup_buttons()
            console.print("[bold]INFO:[/bold] Using real buttons")
        else:
            console.print("[bold]INFO:[/bold] Running in TEST mode")
            console.print(
                "[bold]INFO:[/bold] Using keys (g - green, b - blue, r - red) to simulate buttons"
            )
            self.start_keyboard_listener()
        # Dependencies with their respective installation commands - TODO: Not sure these are needed by PyGame
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
        if not self.is_rpi:
            print("GPIO setup is not available on non-RPi hardware.")
            return

        # RPi-specific GPIO setup code...
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
                console.print(f"[bold]INFO:[/bold] {command} is installed.")
            except subprocess.CalledProcessError:
                console.print(
                    f"ERROR: {command} is not installed. Please install it using: '{info['install']}'"
                )
                all_dependencies_installed = False
        return all_dependencies_installed

    def check(self, max_duration_seconds=10, progress_length=50):
        """Test the equipment setup, including button press detection.
        Reports success only if all three button/key presses are detected."""
        if self.is_rpi:
            console.print("\n[bold red]INFO: Running on RaspberryPi device[/bold red]")
        else:
            console.print("\n[bold]INFO: Running on non-RaspberryPi device[/bold]")
        console.print("\n[bold]INFO:[/bold] Testing equipment setup...")
        console.print("      - Checking command line (non-Python) dependencies")

        if not self.check_non_python_dependencies():
            console.print("[bold red]ERROR:[/bold red] Missing dependencies. Exiting test.")
            return  # Exit the method if dependencies are missing

        # Temporarily override callbacks for testing
        original_callbacks = self.button_press_callbacks.copy()
        pressed_buttons = set()  # To track successfully pressed buttons

        def test_callback(colour):
            nonlocal pressed_buttons
            pressed_buttons.add(colour)
            console.print(f"\n[bold]{colour.capitalize()}[/bold] button/key detected!", style=colour)

        for colour in self.button_press_callbacks.keys():
            console.print(f"\nPlease press the [bold]{colour}[/bold] button/key now...", style=colour)
            console.print("Progress: ", end="")

            # Override the callback for the current button to provide immediate feedback
            self.button_press_callbacks[colour] = lambda colour=colour: test_callback(colour)

            # Display progress bar and wait for button press or timeout

            start_time = time.time()
            while time.time() - start_time < max_duration_seconds and colour not in pressed_buttons:
                elapsed_time = time.time() - start_time
                progress = int((elapsed_time / max_duration_seconds) * progress_length)
                console.print(
                    "#" * progress + "-" * (progress_length - progress), end="\r", style=colour
                )
                time.sleep(0.1)

            if colour not in pressed_buttons:
                console.print(
                    f"\n[bold yellow]WARNING:[/bold yellow] No {colour} button/key press detected.",
                    style=colour,
                )

        # Restore original callbacks
        self.button_press_callbacks = original_callbacks

        # Check if all buttons were pressed
        if len(pressed_buttons) == len(self.button_press_callbacks):
            console.print("\n[bold green]SUCCESS:[/bold green] All button/key presses detected.")
            console.print("\n[bold]INFO:[/bold] Testing completed - [bold green]OK[/bold green]")
        else:
            console.print("\n[bold red]FAILURE:[/bold red] Not all button/key presses were detected.")


        # Initialize the TextToSpeechGoogle class for the TTS functionality check
        tts_google = TextToSpeechGoogle()

        # Perform the TTS functionality check
        try:
            tts_google.speak("Please confirm if you can hear this message by typing 'y'.")
            user_response = input("Did you hear the spoken message? (y/n): ").strip().lower()
            if user_response[0] != "y":
                console.print(
                    "[bold red]ERROR:[/bold red] Text-to-speech functionality check failed. User did not confirm hearing the message."
                )
                return  # Exit the method if the user did not confirm hearing the TTS message
            console.print("[bold green]SUCCESS:[/bold green] Text-to-speech functionality check passed.")
        except Exception as e:
            console.print(f"[bold red]ERROR:[/bold red] Text-to-speech functionality check failed: {e}")
            return  # Exit the method if the TTS check fails due to an exception


if __name__ == "__main__":
    equipment = Equipment(test_mode=True)
    equipment.check()
