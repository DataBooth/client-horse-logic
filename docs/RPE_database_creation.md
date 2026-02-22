# How the RPE DuckDB database is created
This document describes how the RPE DuckDB database (e.g. `data/Experiments_RPE_2023_Q4.ddb`) is generated in this repository.

## Overview
The RPE database is created by running the Jupyter notebook `notebooks/logfile-to-database-RPE.ipynb`.

At a high level, the notebook:
1. Loads project configuration (paths, database filename template, etc.) from `project_config.yaml`.
2. Connects to DuckDB using the configured database path.
3. Creates the RPE schema (tables) by executing `sql/create_experiment_tables_ddb.sql`.
4. Loads a curated list of RPE log files and parses each logfile.
5. Inserts parsed experiment/trial/event records into DuckDB.

## Key files
- `project_config.yaml`
  - Defines the database path template:
    - `database.path: data/Experiments_{experiment_type}_2023_Q4.ddb`
  - For RPE this resolves to:
    - `data/Experiments_RPE_2023_Q4.ddb`

- `src/horse_logic/project.py`
  - `Project` is responsible for:
    - finding the project root
    - initialising directory paths
    - determining the DuckDB file path from `project_config.yaml`
    - creating a DuckDB connection (`duckdb.connect(...)`)
    - running the schema SQL via `create_tables_from_sql_file(...)`

- `sql/create_experiment_tables_ddb.sql`
  - Creates the RPE tables:
    - `Experiments`
    - `Trials`
    - `Events`

- `src/horse_logic/logfiles.py`
  - Parsing and insertion logic:
    - `Logfile.parse_filename_components()` (RPE filename parsing)
    - `Logfile.parse_parameters()` (extracts `PARAMETERS` block)
    - `Logfile.parse_trials_and_events()` (extracts trials and events)
    - `Logfile.insert_record_to_database()` (inserts dataclass records into DuckDB)

- `notebooks/logfile-to-database-RPE.ipynb`
  - Orchestrates the end-to-end process.

## Creation process (step-by-step)
### 1) Initialise the project for RPE
The notebook initialises a `Project` with `experiment_type="RPE"`.

This initialisation:
- resolves the database file path using the template in `project_config.yaml`
- prepares directory paths (data, sql, notebooks, output, logfiles)

Important: `Project.__init__()` defaults to `delete_existing_db=True`.
- If the target database file already exists, it will be deleted before a new connection is created.
- If you want to preserve an existing database, pass `delete_existing_db=False` when constructing `Project`.

### 2) Create tables by executing the schema SQL
The notebook calls:
- `project.create_tables_from_sql_file("create_experiment_tables_ddb.sql")`

That method reads `sql/create_experiment_tables_ddb.sql` and executes it against the DuckDB connection.

### 3) Determine which log files to load
The notebook loads log files from the configured RPE logfiles directory:
- `project_config.yaml: directories.logfiles.path.RPE`

It then builds a list of log files to load (including an additional “extra excludes” list in the notebook).

### 4) Parse logfiles and insert into DuckDB
For each logfile, the notebook:
- parses experiment metadata from the filename
- looks up cohort/subject information (from the cohort spreadsheet)
- parses parameters
- parses trials and events
- inserts rows into DuckDB tables (`Experiments`, `Trials`, `Events`)

The notebook inserts records one-by-one using `Logfile.insert_record_to_database()`.

## DuckDB version notes
### What DuckDB version was used to generate the database?
When the notebook runs, it logs the DuckDB version of the engine being used at that time (via `SELECT version();`).

If you need the historical version for a specific build, check the notebook output from the run that produced the database.

### How to check what version is being used to read the database today
If you open the database with a particular DuckDB installation and run `SELECT version();`, the result is the version of the engine doing the reading.

For example (one-off, using `uv`):
```sh
uv run --with duckdb python -c "import duckdb; con=duckdb.connect('data/Experiments_RPE_2023_Q4.ddb', read_only=True); print(con.execute('select version()').fetchone()[0])"
```

## Outputs
The primary output is the DuckDB database file:
- `data/Experiments_RPE_2023_Q4.ddb`

The notebook also writes intermediate CSVs into the configured output directory:
- `notebooks/results/RPE/`
