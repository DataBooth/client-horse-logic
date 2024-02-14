import pprint
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    import RPi.GPIO as GPIO
    from PiicoDev_CAP1203 import PiicoDev_CAP1203
    from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver

    RPI_MODE = True
except ImportError:
    RPI_MODE = False
    print("\n**** Running in non-RPi mode for testing only ****\n")


if RPI_MODE:
    DATA_DIR = "/home/horselogic/Code/data"
else:
    DATA_DIR = "/Users/mjboothaus/code/github/databooth/horse-logic/data"  # Testing only


def initialise_data_dir():
    """
    Initialises the data directory.

    This function initialises the data directory by calling the `set_directory` function
    with the `DATA_DIR` variable as the argument.

    Returns:
        str: The path to the data directory.
    """
    data_dir = set_directory(DATA_DIR)
    return data_dir


class Button:
    """
    A class representing a button connected to a Raspberry Pi GPIO pin.

    Attributes:
        pin (int): The GPIO pin number to which the button is connected.

    Methods:
        __init__(self, pin):
            Initialises a Button object with the specified GPIO pin. Sets up the GPIO pin as an input with a pull-up resistor.

        is_pressed(self):
            Returns True if the button is pressed (GPIO pin is low), otherwise returns False.
    """

    def __init__(self, pin):
        """
        Initialises a Button object with the specified GPIO pin. Sets up the GPIO pin as an input with a pull-up resistor.

        Args:
            pin (int): The GPIO pin number to which the button is connected.
        """
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def is_pressed(self):
        """
        Returns True if the button is pressed (GPIO pin is low), otherwise returns False.
        """
        return GPIO.input(self.pin) == GPIO.LOW


def initialise_GPIO_buttons(RPi=RPI_MODE):
    """
    Initialises GPIO pins for buttons on a Raspberry Pi.

    Args:
        RPi (bool, optional): A boolean indicating whether the code is running on a Raspberry Pi or not.
                              Default is RPI_MODE which is set to False if the RPi.GPIO module is not imported.

    Returns:
        tuple: A tuple containing the GPIO object and instances of the Button class for each button if the code is running on a Raspberry Pi.
               If the code is not running on a Raspberry Pi, it returns None for all the variables.
    """

    if RPi:
        # Set up GPIO pins for buttons
        GPIO.setmode(GPIO.BCM)
        butpin_green = 6  # Green button
        butpin_blue = 7  # Blue button
        butpin_red = 12  # Red button

        # Set up GPIO pins for input with an internal pull-up resistor
        GPIO.setup(butpin_green, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(butpin_blue, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(butpin_red, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        green_button = Button(butpin_green)
        blue_button = Button(butpin_blue)
        red_button = Button(butpin_red)
        return GPIO, green_button, blue_button, red_button
    else:
        return None, None, None, None


# need a description of what this is?
def elapsed_seconds(start_time):
    """
    Calculate the duration in seconds between the current time and a given start time.

    Args:
        start_time (datetime): A datetime object representing the start time.

    Returns:
        float: The duration in seconds between the current time and the start_time.
    """
    delta_since_start = datetime.now() - start_time
    duration_since_start = delta_since_start.total_seconds()
    return duration_since_start


def set_directory(dir_name):
    """
    Check if the input directory exists and return a Path object representing the directory.

    Args:
        dir_name (str or Path): The name or path of the directory to be checked.

    Returns:
        Path: The Path object representing the input directory.

    Raises:
        TypeError: If dir_name is not a string or a Path object.
        FileNotFoundError: If the specified directory does not exist.
    """
    if not isinstance(dir_name, (str, Path)):
        raise TypeError("dir_name must be a string or a Path object.")
    if not Path(dir_name).exists():
        raise FileNotFoundError(f"The specified directory {dir_name} does not exist.")
    return Path(dir_name)


def create_output_filenames(subject_name, trial_number, trainer_number):
    """
    Generate the names for the log file and quantity file based on the subject name, trial number, and trial type.

    Args:
        subject_name (str): The name of the subject.
        trial_number (int): The number of the trial.
        trainer_number (str): The type of the trial.

    Returns:
        tuple: A tuple containing the name of the log file and the name of the quantity file.

    Example:
        subject_name = "John"
        trial_number = 1
        trainer_number = "preliminary"
        log_file, quantity_file = create_output_filenames(subject_name, trial_number, trainer_number)
        print(log_file)  # Output: Experiment_2022-01-01T12:00:00_John_1_preliminary.log
        print(quantity_file)  # Output: Experiment_2022-01-01T12:00:00_John_1_preliminary.csv
    """
    LOGFILE_PREFIX = "Experiment"
    file_name = (
        f"{LOGFILE_PREFIX}_{datetime.now().isoformat()}_{subject_name}_{trial_number}_{trainer_number}"
    )
    return f"{file_name}.log", f"{file_name}.csv"


def log_event(
    event_name,
    data_dir,
    log_file,
    event_time=None,
    echo_to_console=True,
):
    """
    Log an event in an experiment.

    Args:
        event_name (str): The name or description of the event to be logged.
        data_dir (str): The directory where the log file and quantity file will be stored.
        log_file (str): The name of the log file.
        event_time (str, optional): The timestamp of the event. If not provided, the current timestamp will be used.
        echo_to_console (bool, optional): Whether to print the event details to the console. Default is True.

    Raises:
        FileNotFoundError: If the data directory does not exist.

    Returns:
        None
    """
    if not Path(data_dir).exists():
        raise FileNotFoundError(f"Data directory {data_dir} does not exist.")
    if event_time is None:
        event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    with open(Path(data_dir) / log_file, "a") as flog:
        flog.write(f"{event_time}: {event_name}\n")
    if echo_to_console:
        print(f"Logged - {event_time}: {event_name}\n")
    return None


# date_time,subject_name,trial_number,trainer_number,trial_number,quantity_name,quantity_value
def log_quantity(
    quantity_name,
    quantity_value,
    subject_name,
    trial_number,
    trainer_number,
    data_dir,
    quantity_file,
    quantity_time=None,
    echo_to_console=True,
):
    """
    Logs a quantity value along with relevant information to a CSV file.

    NOTE: The format/content/order of the information written in this function should
    match the header defined in the create_log_quantity_header_file() function

    Args:
        quantity_name (str): The name of the quantity being logged.
        quantity_value (float or int): The value of the quantity being logged.
        subject_name (str): The name of the subject.
        trial_number (int): The number of the trial.
        trainer_number (str): The type of the trial.
        trial_number (int): The number of the trial.
        data_dir (str): The directory where the data is stored.
        quantity_file (str): The name of the quantity file.
        quantity_time (str, optional): The time of the quantity measurement. If not provided, the current time is used.
        echo_to_console (bool, optional): Whether to print the logged quantity to the console. Default is True.

    Raises:
        FileNotFoundError: If the data directory does not exist.

    Returns:
        None
    """
    if not Path(data_dir).exists():
        raise FileNotFoundError(f"Data directory {data_dir} does not exist.")
    if quantity_time is None:
        quantity_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    with open(Path(data_dir) / quantity_file, "a") as fq:
        csv_str = f"{quantity_time},{subject_name},{trial_number},{trainer_number},{trial_number},{quantity_name},{quantity_value}\n"
        fq.write(csv_str)
    if echo_to_console:
        print(f"Quantity recorded - {quantity_time}: {csv_str}")
    return None


def create_log_quantity_header_file(data_dir, quantity_header_file="experiment_quantity_header.csv"):
    """
    Creates a header file for logging experiment quantity data.

    Args:
    - data_dir (str): The directory where the experiment data will be stored.
    - quantity_header_file (str, optional): The name of the quantity header file. Default is "experiment_quantity_header.csv".

    Returns:
    - None

    This function is called during experiment_setup()

    Code Analysis:
    - Define the header string for the quantity file.
    - Open the quantity header file in write mode.
    - Write the header string to the file.
    - Print the path of the created quantity header file.
    """
    quantity_header = (
        "date_time,subject_name,trial_number,trainer_number,trial_number,quantity_name,quantity_value\n"
    )
    with open(Path(data_dir) / quantity_header_file, "w") as fh:
        fh.write(quantity_header)
    print(f"Quantity header file created: {(Path(data_dir) / quantity_header_file).as_posix()}")
    return None


def log_trial_parameters(parameters, data_dir, log_file):
    """
    Logs the trial parameters by writing them to a log file.

    Args:
        parameters (any type): The trial parameters to be logged.
        data_dir (str): The directory where the log file will be stored.
        log_file (str): The name of the log file.

    Returns:
        None
    """
    pformatted = pprint.pformat(parameters)
    with open(Path(data_dir) / log_file, "a") as f:
        f.write(f"PARAMETERS:\n{pformatted}\n")
    print(f"Logged - PARAMETERS:\n{pformatted}\n")
    return None


def set_subject_name(data_dir):
    """
    Prompts the user to enter the subject name and retrieves the next trial number for that subject from a tracking file.

    Args:
        data_dir (str): The directory where the tracking file is located.

    Returns:
        tuple: A tuple containing the subject name (str), the next trial number (int), and the updated tracking file as a DataFrame.

    Example:
        subject_name, next_trial_number, experiment_subjects_df = set_subject_name(data_dir)
    """

    subject_name = False
    print("\nStarting experiment:")
    print("\n  Press Ctrl-C to exit the experiment\n")
    print("  Ensure the subject is settled and ready for the experiment\n")

    while not subject_name:
        subject_name_in = input("\nEnter subject name: ")
        subject_name, next_trial_number, experiment_subjects_df = get_next_trial_number(
            subject_name_in, data_dir
        )
    return subject_name, next_trial_number, experiment_subjects_df


def get_next_trial_number(subject_name, data_dir, subjects_file="experiment_subjects.xlsx"):
    """
    Retrieves the next trial number for a given subject name from a tracking file.

    Args:
        subject_name (str): The name of the subject for which to retrieve the next trial number.
        data_dir (str): The directory where the tracking file is located.
        subjects_file (str, optional): The name of the tracking file. Default is "experiment_subjects.xlsx".

    Returns:
        tuple: A tuple containing the subject name, the next trial number, and the updated tracking file as a DataFrame.

    Raises:
        FileNotFoundError: If the tracking file does not exist in the specified directory.
    """
    if not (Path(data_dir) / subjects_file).exists():
        raise FileNotFoundError(f"Tracking file {Path(data_dir) / subjects_file} does not exist.")
    # Read in the tracking file
    experiment_subjects_df = pd.read_excel(Path(data_dir) / subjects_file)
    experiment_subjects_df["subject_name_clean"] = experiment_subjects_df["subject_name"].apply(
        lambda name: name.lower().replace(" ", "")
    )
    subject_names = [name.lower() for name in experiment_subjects_df["subject_name"].values.tolist()]
    # Amend to allow for subject names with spaces
    subject_names = [name.replace(" ", "") for name in subject_names]
    subject_name_clean = subject_name.lower().replace(" ", "")
    if subject_name_clean not in subject_names:
        print(
            f"Subject {subject_name} not found in tracking file.\nSee {(Path(data_dir) / subjects_file).as_posix()}."
        )
        return False, 0, 0
    next_trial_number = (
        experiment_subjects_df[experiment_subjects_df["subject_name_clean"] == subject_name_clean][
            "last_trial_number"
        ].values[0]
        + 1
    )
    experiment_subjects_df.loc[
        experiment_subjects_df["subject_name_clean"] == subject_name_clean,
        "last_trial_number",
    ] = next_trial_number
    return subject_name_clean, next_trial_number, experiment_subjects_df


def update_subjects_xlsx(data_dir, experiment_subjects_df, subjects_file):
    """
    Update an Excel file containing information about experiment subjects.

    Args:
        data_dir (str): The directory where the experiment data is stored.
        experiment_subjects_df (DataFrame): A DataFrame containing information about the experiment subjects.
        subjects_file (str): The name of the Excel file that stores the subjects' information.

    Returns:
        None

    Example Usage:
        update_subjects_xlsx(data_dir, experiment_subjects_df, "experiment_subjects.xlsx")

    This code updates the "experiment_subjects.xlsx" file in the `data_dir` directory
    with the information in the `experiment_subjects_df` DataFrame.
    It removes a column from the DataFrame and saves the updated DataFrame to the Excel file.
    """
    experiment_subjects_df.drop(columns=["subject_name_clean"], inplace=True)
    experiment_subjects_df.to_excel(Path(data_dir) / subjects_file, index=False)
    return None


def confirm_experiment_details(subject_name, trial_number, trainer_number):
    """
    Confirms the experiment details with the user.

    Args:
        subject_name (str): The name of the subject.
        trial_number (int): The trial number.
        trainer_number (str): The type of experiment.

    Returns:
        True if the user confirms the experiment details are correct, False otherwise.
    """
    print(f"\nSubject name: {subject_name}")
    print(f"Trial number: {trial_number}")
    print(f"Experiment type: {trainer_number}")
    confirm = input("\nAre the details ok for this trial (Y (or return) - continue / N - exit)?: ")
    if confirm == "" or confirm.lower()[0] == "y":
        return True
    else:
        return False


@dataclass
class Parameter:
    """
    A class representing a specific parameter used in an experiment.

    Attributes:
        name (str): The name of the parameter.
        val (float): The value of the parameter.
        unit (str): The unit of measurement for the parameter.
        minimum_value (float): The minimum allowed value for the parameter.
        maximum_value (float): The maximum allowed value for the parameter.
        description (str): A description of the parameter.
    """

    name: str
    val: float
    unit: str
    minimum_value: float
    maximum_value: float
    description: str


def parse_text_for_na(value):
    """
    Check if a value is a missing value (NaN) and return the value or an empty string.

    Parameters:
    value (any): The value to be checked for NaN.

    Returns:
    str: The original value if it is not NaN.
         An empty string if the value is NaN.
    """

    if pd.isna(value):
        return ""
    else:
        return value


def get_parameter(name, experiment_parameters_df):
    """
    Retrieves a specific parameter from a DataFrame containing experiment parameters.

    Args:
        name (str): The name of the parameter to retrieve.
        experiment_parameters_df (DataFrame): The DataFrame containing the experiment parameters.

    Returns:
        Parameter: The parameter with the specified name, or None if the parameter does not exist in the DataFrame.
    """
    row = experiment_parameters_df.loc[experiment_parameters_df["name"] == name]
    if row.drop(columns=["name"]).isnull().values.all():
        return None
    return Parameter(
        name=name,
        val=row["value"].values[0],
        minimum_value=row["minimum_value"].values[0],
        maximum_value=row["maximum_value"].values[0],
        unit=parse_text_for_na(row["unit"].values[0]),
        description=parse_text_for_na(row["description"].values[0]),
    )


def load_validate_experiment_parameters(data_dir, parameters_xlsx="experiment_parameters.xlsx"):
    """
    Load and validate experiment parameters from an Excel file.

    Args:
        data_dir (str): The directory where the experiment data is stored.
        parameters_xlsx (str, optional): The name of the Excel file containing the experiment parameters.
            Defaults to "experiment_parameters.xlsx".

    Raises:
        FileNotFoundError: If the experiment parameters Excel file does not exist in the specified data directory.

    Returns:
        dict: A dictionary containing the validated parameter values.
    """

    if not Path(data_dir / parameters_xlsx).exists():
        raise FileNotFoundError(f"{parameters_xlsx} does not exist")

    experiment_parameters_df = pd.read_excel(Path(data_dir / parameters_xlsx))
    par = {}
    for name in experiment_parameters_df["name"]:
        parameter = get_parameter(name, experiment_parameters_df)
        if parameter is not None:
            if pd.isna(parameter.val):
                print(f"WARNING: {parameter.name} is UNDEFINED")
                par[name] = "-- UNDEFINED --"
            else:
                # check if parameter is numeric
                if isinstance(parameter.val, (int, float)):
                    if (
                        parameter.val < parameter.minimum_value
                        or parameter.val > parameter.maximum_value
                    ):
                        print(f"{parameter.name} is out of range: {parameter.val} {parameter.unit}")
                    print(f"{parameter.name}: {parameter.val} {parameter.unit} - Validated")
                else:
                    print(f"{parameter.name} is not numeric: {parameter.val}")
                par[name] = parameter.val
    return par

def read_experiment_schedule(schedule_xlsx="exp_phase2_schedule.xlsx", data_dir=DATA_DIR):
    """
    Reads the RewardSchedule and TrainerSchedule tables from an Excel workbook into DataFrames.

    Args:
        schedule_xlsx (str, optional): The name of the Excel file containing the schedules.
        data_dir (str, optional): The directory where the experiment data is stored.

    Returns:
        tuple: A tuple containing the DataFrames for RewardSchedule and TrainerSchedule.
    """
    schedule_xlsx_path = Path(data_dir) / schedule_xlsx
    if not schedule_xlsx_path.exists():
        raise FileNotFoundError(f"{schedule_xlsx_path} does not exist")

    # Read the RewardSchedule table
    reward_schedule_df = pd.read_excel(
        schedule_xlsx_path,
        sheet_name='ExperimentSchedule',
        skiprows=8,  # Skip rows before the header row
        nrows=21,    # Number of rows to read, excluding the header
        usecols="A:G"  # Columns to read
    )

    # Read the TrainerSchedule table
    trainer_schedule_df = pd.read_excel(
        schedule_xlsx_path,
        sheet_name='ExperimentSchedule',
        skiprows=31,  # Skip rows before the header row
        nrows=21,     # Number of rows to read, excluding the header
        usecols="A:G"  # Columns to read
    )

    # Convert boolean columns to actual booleans for RewardSchedule
    for col in reward_schedule_df.columns[1:]:  # Assuming the first column is not boolean
        reward_schedule_df[col] = reward_schedule_df[col].apply(pd.to_numeric, downcast='unsigned', errors='coerce').astype('bool')

    # Convert label columns to integers for TrainerSchedule
    for col in trainer_schedule_df.columns[1:]:  # Assuming the first column is not labels
        trainer_schedule_df[col] = trainer_schedule_df[col].apply(pd.to_numeric, downcast='integer', errors='coerce').fillna(0).astype(int)

    return reward_schedule_df, trainer_schedule_df

def setup_experiment(data_dir=DATA_DIR):
    """
    Initialises the necessary components and parameters for an experiment.

    Args:
        data_dir (str, optional): The directory where the experiment data will be stored.

    Returns:
        tuple: A tuple containing the subject name, trial number, trial type, experiment parameters, touch sensor object, servo motor object, data directory, log file name, and quantity file name.

    Example:
        subject_name, trial_number, trainer_number, p, touchSensor, servo, data_dir, log_file, quantity_file = setup_experiment()

    """

    #TODO - read in Experiment schedule

    data_dir = initialise_data_dir()
    create_log_quantity_header_file(data_dir)
    p = load_validate_experiment_parameters(data_dir)
    subject_name, trial_number, experiment_subjects_df = set_subject_name(data_dir)
    if not confirm_experiment_details(subject_name, trial_number, trainer_number):
        print("\nExiting - user terminated trial...\n")
        sys.exit()
    update_subjects_xlsx(data_dir, experiment_subjects_df, subjects_file="experiment_subjects.xlsx")
    log_file, quantity_file = create_output_filenames(subject_name, trial_number, trainer_number)
    log_trial_parameters(p, data_dir, log_file)
    comment = input("\nEnter any comments for this trial: ")
    if comment == "":
        comment = "None"
    log_event(f"Comment: {comment}", data_dir, log_file)
    log_event(f"Data directory: {data_dir}", data_dir, log_file)
    log_event(f"Log file: {log_file}", data_dir, log_file)
    log_event(f"Quantity file: {quantity_file}", data_dir, log_file)
    log_event(f"Subject {subject_name}; Trial # {trial_number}; Trainer #{trainer_number} started...", data_dir, log_file)
    return subject_name, trial_number, trainer_number, p, data_dir, log_file, quantity_file
