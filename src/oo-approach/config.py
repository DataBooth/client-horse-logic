import argparse
import toml
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Run the experiment in testing or production mode.")
    parser.add_argument(
        "--testing-mode", action="store_true", help="Run in testing mode without actual hardware."
    )
    args = parser.parse_args()
    return args


def load_config(config_file_path="config.toml", command_line_args=None):
    if not Path(config_file_path).is_file():
        raise FileNotFoundError(f"The configuration file {config_file_path} does not exist.")
    with open(config_file_path, "r") as config_file:
        config = toml.load(config_file)

    # Override TESTING_MODE from config.toml if specified in command line arguments
    if command_line_args and command_line_args.testing_mode:
        config["TESTING_MODE"] = True
    return config
