from config import load_config

# Load the configuration and check for TESTING_MODE

config = load_config()
TESTING_MODE = config.get("TESTING_MODE", False)


if not TESTING_MODE:
    import RPi.GPIO as GPIO
    from PiicoDev_CAP1203 import PiicoDev_CAP1203
    from PiicoDev_Servo import PiicoDev_Servo
else:
    # Mock implementations or alternative implementations for testing
    class GPIO:
        BCM = None
        IN = None
        PUD_UP = None

        @staticmethod
        def setup(pin, direction, pull_up_down=None):
            pass

        @staticmethod
        def input(pin):
            return False  # Default to not pressed

        @staticmethod
        def cleanup():
            pass

    class PiicoDev_CAP1203:
        def __init__(self, touchmode="single", sensitivity=5):
            pass

        def is_touched(self):
            return False  # Default to not touched

    class PiicoDev_Servo:
        def __init__(self, channel):
            self.channel = channel

        def dispense_feed(self):
            pass  # Logic for testing without actual hardware


class Button:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_pressed(self):
        return GPIO.input(self.pin) == GPIO.LOW


class Servo:
    def __init__(self, channel):
        self.servo = PiicoDev_Servo(channel)

    def dispense_feed(self):
        # Logic to dispense feed
        pass


class TouchSensor:
    def __init__(self, sensitivity):
        self.touch_sensor = PiicoDev_CAP1203(touchmode="single", sensitivity=sensitivity)

    def is_touched(self):
        # Logic to check if the sensor is touched
        pass
