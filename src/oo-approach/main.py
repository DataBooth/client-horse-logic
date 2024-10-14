from experiment import Experiment
from experiment_helper import DataManager, SoundManager, Button, Servo, TouchSensor
from config import parse_args, load_config
from pathlib import Path


def main():
    args = parse_args()
    config = load_config(config_file_path=(Path.cwd() / "config.toml").as_posix(), command_line_args=args)
    data_manager = DataManager(config["DATA_DIR"])
    sound_manager = SoundManager()
    hardware = {
        "buttons": {
            "green": Button(config["GREEN_BUTTON_PIN"]),
            "blue": Button(config["BLUE_BUTTON_PIN"]),
            "red": Button(config["RED_BUTTON_PIN"]),
        },
        "servo": Servo(config["SERVO_CHANNEL"]),
        "touch_sensor": TouchSensor(config["SENSITIVITY"]),
    }


experiment = Experiment(config)
experiment.run()


if __name__ == "__main__":
    main()
