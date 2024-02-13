import subprocess
from text_to_speech import TextToSpeechGoogle

class HardwareTester:
    def __init__(self):
        self.tts = TextToSpeechGoogle()
        self.is_rpi = self.check_if_rpi()

    def check_if_rpi(self):
        """Check if the current platform is a Raspberry Pi."""
        try:
            with open('/sys/firmware/devicetree/base/model', 'r') as f:
                if 'Raspberry Pi' in f.read():
                    return True
        except Exception:
            return False

    def check_dependency(self, command, install_command):
        """Check if a command-line dependency is installed, and advise on how to install it if not."""
        try:
            subprocess.run([command, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"{command} is installed.")
        except subprocess.CalledProcessError:
            print(f"{command} is not installed. Please install it using: '{install_command}'")

    def test_hardware(self):
        """Test the hardware setup."""
        if self.is_rpi:
            print("Running on Raspberry Pi. Checking for necessary dependencies...")
            self.check_dependency('espeak', 'sudo apt-get install espeak')
            self.check_dependency('ffmpeg', 'sudo apt-get install ffmpeg')
        else:
            print("Running on macOS. Skipping additional dependency checks.")

if __name__ == "__main__":
    tester = HardwareTester()
    tester.test_hardware()
