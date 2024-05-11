## Overview

This code defines two classes:

- `Logfile` and
- `Logs`

along with several helper functions. The `Logfile` class represents a log file and provides methods to parse its filename components. The `Logs` class represents a collection of log files and provides methods to load and manipulate them.

### Inputs

- `file_name`: A string representing the name of a log file.
- `file_contents`: A list of strings representing the contents of a log file.
- `log_contents`: A string representing the contents of a log file.
- `sql_file_path`: A string representing the path to an SQL file.
- `db_connection`: A database connection object.

### Code Flow

1. The `Logfile` class has an `__init__` method that initialises the object attributes `file_name`, `file_contents`, and `num_lines`.
2. The `parse_filename_components` method of the Logfile class uses regular expressions to extract components from the file name, such as suffix, datetime, subject name, trial number, and experiment type.
3. The `parse_parameters` function uses regular expressions to extract a parameters block from the log contents and converts it into a dictionary.
4. The `parse_trials_and_events` function uses regular expressions to extract trial numbers and events from the log contents and returns them as lists of dictionaries.
5. The `create_tables_from_sql` function reads an SQL file, executes the SQL commands in it using a database connection, and prints a success message.
6. The `Logs` class has an `__init__` method that initialises the object attributes path, patterns, include, logfile_ext, logfiles, included_files, and excluded_files.
7. The `load_logfiles` method of the `Logs` class uses the glob module to find log files matching the specified patterns in the specified path, reads their contents, and creates `Logfile` objects for them.
8. The `handle_specific_files` method of the `Logs` class handles specific file names to include or exclude from the log files list.
9. The `create_filename_components_dataframe` method of the `Logs` class creates a pandas DataFrame from the filename components of the specified file list.

### Outputs

- Logfile objects representing individual log files.
- Lists of dictionaries representing parsed parameters, trials, and events.
- Success message when creating tables from an SQL file.
- A pandas DataFrame representing the filename components of log files.

### Usage example

- Create a Logfile object
`logfile = Logfile("example.log", ["line 1", "line 2", "line 3"])`

- Parse filename components
`components = logfile.parse_filename_components()`

- Parse parameters from log contents
`params = parse_parameters(log_contents)`

- Parse trials and events from log contents
`trials, events = parse_trials_and_events(log_contents)`

- Create tables from an SQL file
`create_tables_from_sql("example.sql", db_connection)`

- Create a Logs object
`logs = Logs("path/to/logs", "*.log")`

- Load log files from the directory
`logs.load_logfiles()`

- Handle specific files to include or exclude
`logs.handle_specific_files(["file1.log", "file2.log"], include=True)`

- Create a DataFrame of filename components
`df = logs.create_filename_components_dataframe(logs.included_files)`
