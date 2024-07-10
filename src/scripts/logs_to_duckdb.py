from horse_logic.logfiles import (
    Logfile,
    create_tables_from_sql,
    parse_parameters,
    parse_trials_and_events,
)
import duckdb
import os
from itertools import count


# Main function to process log files and insert data into DuckDB
def process_log_files(log_directory, sql_file_path, db_path=":memory:"):
    # Connect to DuckDB
    con = duckdb.connect(db_path)

    # Create tables from the SQL file
    create_tables_from_sql(sql_file_path, con)

    # Create a counter starting at 1 - for use as primary key in Experiments
    exp_id = count(start=1)
    param_id = count(start=1)
    trial_id = count(start=1)
    event_id = count(start=1)

    # Process each log file
    for log_file_name in os.listdir(log_directory):
        if log_file_name.endswith(".log"):
            log_file_path = os.path.join(log_directory, log_file_name)
            with open(log_file_path, "r") as log_file:
                log_contents = log_file.read()

            # Parse experiment details
            logfile = Logfile(log_file_name, log_contents)
            experiment_details = logfile.parse_filename_components()

            # Parse parameters
            parameters = parse_parameters(log_contents)

            # Parse trials and events
            trials, events = parse_trials_and_events(log_contents)

            # Insert experiment details into the database
            # Assuming 'Experiments' table exists and has columns matching the keys in experiment_details
            # Exclude the ExperimentID in the column list and the VALUES list

            trial_number = (
                experiment_details["trial_number"]
                if experiment_details["trial_number"] is not None
                else 0
            )

            # Insert experiment details into the database and get the last inserted ExperimentID

            result = con.execute(
                "INSERT INTO Experiments (ExperimentID, SubjectName, SessionNumber, ExperimentType, Comment, DateTime, LogFileName) VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING ExperimentID",
                (
                    next(exp_id),
                    experiment_details["subject_name"],
                    trial_number,
                    experiment_details["experiment_type"],
                    "TODO_Comment",
                    experiment_details["datetime"],
                    log_file_name,
                ),
            ).fetchone()

            last_experiment_id = result[0] if result else None

            # Get the last inserted ExperimentID to use as a foreign key
            # experiment_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]

            # Insert parameters into the database
            # Assuming 'Parameters' table exists and has columns for ExperimentID, ParameterName, and ParameterValue
            for param_name, param_value in parameters.items():
                con.execute(
                    "INSERT INTO Parameters (ParameterID, ExperimentID, ParameterName, ParameterValue) VALUES (?, ?, ?, ?)",
                    (next(param_id), last_experiment_id, param_name, param_value),
                )

            # Insert trials and events into the database
            # Assuming 'Trials' and 'Events' tables exist
            for trial in trials:
                result = con.execute(
                    "INSERT INTO Trials (TrialID, ExperimentID, TrialNumber) VALUES (?, ?, ?) RETURNING TrialID",
                    (next(trial_id), last_experiment_id, trial["TrialNumber"]),
                ).fetchone()
                last_trial_id = result[0] if result else None

                for event in events:
                    if event["TrialNumber"] == trial["TrialNumber"]:
                        con.execute(
                            "INSERT INTO Events (EventID, TrialID, EventType, EventDateTime) VALUES (?, ?, ?, ?)",
                            (next(event_id), last_trial_id, event["EventType"], event["EventDateTime"]),
                        )

            print(f"Data from {log_file_name} has been inserted into the database.")

    # Close the database connection
    con.close()


LOGS_DIR = "/Users/mjboothaus/code/github/databooth/horse-logic/data/results/data_17Jan2020_email_hillydale_equine"
SQL_FILE = "/Users/mjboothaus/code/github/databooth/horse-logic/sql/create_tables_duckdb.sql"
DB_PATH = "/Users/mjboothaus/code/github/databooth/horse-logic/tmp_data/results/experiments_Oct2023.ddb"

# Assuming the Logfile class and parse_filename_components method already exist

# Replace 'path/to/log/directory' with the path to your directory containing log files
# Replace 'path/to/your/sqlfile.sql' with the path to your SQL file
process_log_files(LOGS_DIR, SQL_FILE, DB_PATH)
