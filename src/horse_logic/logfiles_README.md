# Log File Parser and Analyser

This module provides functionality for parsing and analysing log files from various experiments, including RPE (Reward Prediction Error) and CB (Cognitive Bias) experiments.

**NOTE: Only the code for the `RPE` is complete and reasonably well-tested. The `CB` code is incomplete and a work in progress dependent on the final specification of the data items that need to be extracted from the log files.**

## Classes

This code defines two classes:

- `Logfile` and
- `Logs`

along with several helper functions. The `Logfile` class represents a log file and provides methods to parse its filename components. The `Logs` class represents a collection of log files and provides methods to load and manipulate them.

## Features

- Parse log files and extract relevant information
- Handle multiple log files in a directory
- Create DataFrames with parsed filename components
- Parse trials and events from log files
- Create database tables from SQL files

## Dependencies

- pandas
- duckdb
- loguru

## Usage

1. Initialise a `Logs` object with the directory containing log files:

```python
logs = Logs("/path/to/log/files", patterns=["*.log"], include=True)
```

2. Load and parse log files:

```python
logs.load_logfiles()
```

3. Create a DataFrame with filename components:
```python
df = logs.create_filename_components_dataframe(logs.included_files)
```

4. Parse trials and events from a specific log file:
```python
logfile = Logfile("example.log")
trials, events = logfile.parse_trials_and_events()
```

5. Create database tables from a SQL file:
```python
create_tables_from_sql("create_tables.sql", db_connection)
```

### Example Outputs

- Logfile objects representing individual log files.
- Lists of dictionaries representing parsed parameters, trials, and events.
- A pandas DataFrame representing the filename components of log files.
