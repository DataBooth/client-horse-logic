## Setup and running of experiment code

The code is designed to be run on a Raspberry Pi using Python.
The code should be run from the command line using the following command:

```bash
python Final_RPE.py
```

### Dependencies

Other than the standard libraries that are included with all Python distributions, the only additional dependencies required to be installed are:
- `pandas`
- `openpyxl`
which can be installed using the *package manager* in Thony or at the command line using:
```bash
pip install pandas
pip install openpyxl
```

Note that pandas relies on the `numpy` package which required the following tweaks to install after installing `pandas`:

```bash
pip uninstall numpy
sudo apt install libatlas3-base-dev
pip install numpy==1.25.2  [need to confirm version number]
```

The code should be run for each subject (horse) for each session number of specified session type (see details below under Session types).

### Running the code

You are asked a number of questions as part of running each experiment (session). You can terminate the code at any point by typing Ctrl-C. The questions are:

#### Enter subject name

The horses name should be unique (see `data/experiment_subjects.xlsx` below). Any incorrect name will lead to the question being asked again.

#### Choose session type

Choose from one of the four options (a valid response between 1 and 4 is required).

#### Confirm the details

The subject name, session number and experiment type are then displayed. Press Y (or return) to continue of N to exit the code.

The parameters for the session (see `data/experiment_parameters.xlsx` below) are printed to the screen. Check of any UNDEFINED parameters.

#### Comments

You may then (optionally) enter any comments for the experiment. Press return if there are none.

#### Session commences

The session then commences.

### Python code

The two code files are:
- `Final_RPE.py`
- `experiment_helper.py`
- `experiment_sounds.py`

The `experiment_helper.py` file contains the helper functions for the experiment code to hide the details of the
experiment code from the main code. `experiment_sounds.py` contains the paths for each of the sounds for the experiment.

### Data files

#### Inputs

- `data/experiment_subjects.xlsx`
- `data/experiment_parameters.xlsx`

The first workbook is used to specify the names of the subjects (horses) in the experiments
It assumes that the horses have unique names (although it ignores the case and any spaces in the subject names) and that the names are in the first column of the first sheet of the workbook. The workbook also tracks the number of the last session for each subject (horse). Initially the last session will be zero for each subject. The subject name and session number are included in the name of the data and log file for each session.

The parameters for each session are specified in the workbook `data/experiment_parameters.xlsx`.
Each parameter is specified in the `name` column with the corresponding value in the `value` column.
The units for each quantity are not used in the code and are there for reference purposes. For numeric quantities there are the columns `minimum_value` and `maximum_value` which allow for providing a validation range to ensure that `minimum_value <= value <= maximum_value` to minimise/catch errors if
changing the value of numeric parameters. Non-numeric parameters are not validated.

Values in the workbook should be numbers/text and **not formulas**. Any row that is blank, other than possibly a text heading in the `name` column e.g.  _General_ or _Touch sensor_ is ignored.

The information in the remaining columns is not used and is for reference only.

All of the parameters are written at the top of the log file for each subject/session.

#### Log files and quantity recording files

Naming convention for log files and data files is:

 `Experiment_{SESSION_START_TIMESTAMP}_{SUBJECT_NAME}_{SESSION_NUMBER}_{SESSION_TYPE}`

with a `.log` (log file) or `.csv` (quantity recording file) extension.


### Session types

#### RP-A - acquisition of response

- trialLimit = 20 per session, multiple sessions until acquisition criterion
- unlimited time between start tone and touch (or button)
- criterion = n touches in a row that occur under 20 sec from start tone
- no responseTimeout

#### RP-H - habit formation

- trialLimit = 20 fixed trials per session, 3 sessions
- responseTimeout 45s

#### RP-E - extinction of response

- trialLimit = 20, multiple session until extinction criterion
- number of responses in a row
- criterion_seconds = 20s

#### RP-R - reinstatement of response

- trialLimit = 20 per session, multiple sessions until acquisition criterion
- no responseTimeout
