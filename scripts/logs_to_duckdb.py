from horse_logic.logfiles import (
    Logfile,
    create_tables_from_sql,
    parse_parameters,
    parse_trials_and_events,
)
import duckdb
import os


# Main function to process log files and insert data into DuckDB
def process_log_files(log_directory, sql_file_path, db_path=":memory:"):
    # Connect to DuckDB
    con = duckdb.connect(db_path)

    # Create tables from the SQL file
    create_tables_from_sql(sql_file_path, con)

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
            con.execute(
                "INSERT INTO Experiments (SubjectName, SessionNumber, ExperimentType, Comment, DataDirectory, LogFileName) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    experiment_details["subject_name"],
                    experiment_details["trial_number"],
                    experiment_details["experiment_type"],
                    "TODO Comment",
                    "/data/results/data_17Jan2020_email_hillydale_equine",
                    log_file_name,
                ),
            )
            # Get the last inserted ExperimentID to use as a foreign key
            experiment_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]

            # Insert parameters into the database
            # Assuming 'Parameters' table exists and has columns for ExperimentID, ParameterName, and ParameterValue
            for param_name, param_value in parameters.items():
                con.execute(
                    "INSERT INTO Parameters (ExperimentID, ParameterName, ParameterValue) VALUES (?, ?, ?)",
                    (experiment_id, param_name, param_value),
                )

            # Insert trials and events into the database
            # Assuming 'Trials' and 'Events' tables exist
            for trial in trials:
                con.execute(
                    "INSERT INTO Trials (ExperimentID, TrialNumber) VALUES (?, ?)",
                    (experiment_id, trial["TrialNumber"]),
                )
                trial_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]

                for event in events:
                    if event["TrialNumber"] == trial["TrialNumber"]:
                        con.execute(
                            "INSERT INTO Events (TrialID, EventType, EventDateTime) VALUES (?, ?, ?)",
                            (trial_id, event["EventType"], event["EventDateTime"]),
                        )

            print(f"Data from {log_file_name} has been inserted into the database.")

    # Close the database connection
    con.close()


LOGS_DIR = "/Users/mjboothaus/code/github/databooth/horse-logic/data/results/data_17Jan2020_email_hillydale_equine"
SQL_FILE = "/Users/mjboothaus/code/github/databooth/horse-logic/sql/create_tables_duckdb.sql"

# Assuming the Logfile class and parse_filename_components method already exist

# Replace 'path/to/log/directory' with the path to your directory containing log files
# Replace 'path/to/your/sqlfile.sql' with the path to your SQL file
process_log_files(LOGS_DIR, SQL_FILE)
