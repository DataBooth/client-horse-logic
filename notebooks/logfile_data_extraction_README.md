## Overview

The code is responsible for parsing log files and handling specific file names to be either included or excluded (to filter out test or bad data logfiles).

It also creates a dataframe with filename components and calculates time differences for each trial.

### Inputs

`path_logfiles`: The path to the directory containing the log files.
`exclude_file_list`: A list of file names to be excluded.

### Code Flow

1. Initialise the Logs object with the path to the log files and patterns to include or exclude.
2. Print the number of included and excluded log files.
3. Handle specific file names for inclusion or exclusion.
4. Create a dataframe with filename components.
5. Sort the dataframe by subject name and trial number.
6. Drop unnecessary columns from the dataframe.
7. Calculate the time difference between consecutive trials.
8. Convert the trial number column to nullable integer type.
9. Filter the dataframe for a specific subject name and time difference condition.
10. Save the dataframe to a CSV file.
11. Initialise the LogParser object with the log format and directory path.
12. Parse each log file using the LogParser object.
13. Connect to a DuckDB database.
14. Query the database to fetch the data from the "Experiments" table.

### Outputs

- Dataframes containing the included and excluded file names.
- Dataframe with filename components and time differences.
- CSV file containing the dataframe.
- Parsed log files stored in the specified output directory.
- Data fetched from the "Experiments" table in the DuckDB database.

### Usage example

```{python}
path_logfiles = "../data/results/data_17Jan2020_email_hillydale_equine"
exclude_file_list = ["file1_exclude.log", "file2_exclude.log"]

logs = Logs(path=path_logfiles, patterns=["*_test*.log", "*freckle*.log"], include=False)
print(logs)
print(f"Included logfiles: {len(logs.included_files)}")
print(f"Excluded logfiles: {len(logs.excluded_files)}")

logs.handle_specific_files(exclude_file_list, include=False)

df_excluded = pd.DataFrame(logs.excluded_files, columns=["Excluded"])
df_included = pd.DataFrame(logs.included_files, columns=["Included"])

df_file_components = logs.create_filename_components_dataframe(logs.included_files)
df_out = df_file_components.sort_values(by=["subject_name", "trial_number"]).reset_index(drop=True)
df_out.drop(labels=["suffix"], axis=1, inplace=True)
df_out = df_out[["original_filename", "subject_name", "experiment_type", "trial_number", "datetime"]]
df_out["time_diff"] = df_out["datetime"].diff()
df_out["trial_number"] = df_out["trial_number"].astype("Int64")

bonnie_exclude_list = df_out[df_out["time_diff"] < pd.Timedelta("5m")]["original_filename"].tolist()
logs.handle_specific_files(bonnie_exclude_list, include=False)

parser = LogParser(log_format, logs.path, outdir="./parse",  depth=depth, st=st, rex=[])

for logfile in tqdm(logs.included_files, total=len(logs.included_files)):
    try:
        parser.parse(Path(logfile).name)
    except:
        print(f"ERROR: Unable to process {Path(logfile).name}")

con = duckdb.connect(database="/Users/mjboothaus/code/github/databooth/horse-logic/experiments_Oct2023.ddb")
con.query("SELECT * FROM Experiments").fetchdf()
```
