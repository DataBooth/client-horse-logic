# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This repository contains code for behavioural experiments conducted with horses at Charles Sturt University (Wagga Wagga, NSW). The project has two main components:

1. **Experimental control code** - Python scripts that run on Raspberry Pi hardware to control experiments, capture sensor data, and log horse responses to stimuli
2. **Analytics pipeline** - Jupyter notebooks that parse experimental log files, load data into DuckDB databases, and enable analysis via SQL queries

### Experiment Types

**RPE (Response to Positive Expectation)** - measures horse latency responses to various stimuli across four session types:
- **RPE-A (Acquisition)** - horses learn to respond to start tone by touching panel (variable trials/sessions until criterion reached, unlimited response time)
- **RPE-H (Habit)** - habitual responding develops (fixed 20 trials × 3 sessions, 45s response timeout)
- **RPE-E (Extinction)** - response extinguished without food rewards (variable trials/sessions, 20s timeout, criterion of n consecutive no-go responses)
- **RPE-R (Reinstatement)** - touch response reinstated (variable trials/sessions, unlimited response time)

**CB (Cognitive Bias)** - evaluates horse decision-making patterns with training and test sessions:
- Training sessions: fixed block (positive LEFT/RIGHT), randomised Type 1 & 2
- Test sessions: Type 1, 2, 3 (no criterion, 30s timeout vs 20s for training)
- Trials use positive/negative/median/near-positive/near-negative stimuli
- Direction (LEFT/RIGHT) indicates positive stimulus position

## Development Environment

### Dependencies

The project uses **uv** for Python dependency management (originally set up with PDM). Dependencies are defined in `pyproject.toml` (requires Python >= 3.10).

Key dependency groups:
- Production: pandas, DuckDB, matplotlib, loguru, pygame (for Raspberry Pi audio), seaborn, python-dotenv
- `dev` - Jupyter notebooks, black formatter, pre-commit hooks
- `hardware` - Raspberry Pi-specific packages (pigpio, piicodev)
- `util` - Development utilities (pipdeptree)

### Task Automation with justfile

The project uses **just** for task automation. All recipes work cross-platform (macOS, Windows, Linux).

**Notebook execution:**
```bash
just run-notebook notebooks/logfile-reconciliation-RPE.ipynb [keep_py] [capture_output]
just run-notebooks  # Runs both RPE and CB reconciliation notebooks sequentially
```

**Quarto rendering:**
```bash
just render  # Render all notebooks in notebooks/ directory
just quarto notebooks/logfile-reconciliation-RPE.ipynb [quarto_render_dir]  # Render specific notebook
just publish  # Render and publish notebooks to public GitHub Pages repo
just qpreview notebooks  # Preview Quarto project
```

**Database operations:**
```bash
just cp2md local_db remote_db  # Copy local DuckDB database to MotherDuck cloud
```

**Documentation:**
```bash
just convert-md "docs/*.md" docs/output pdf  # Convert markdown to PDF (requires pandoc)
just convert-md "docs/*.md" docs/output html  # Convert markdown to HTML
just extract-sql notebook.ipynb [output.sql]  # Extract SQL statements from notebook
just dir-md [docs/complete_directory_structure.md]  # Generate directory tree markdown
```

**Requirements management:**
```bash
just reqs  # Export requirements.txt from pyproject.toml using PDM
```

### Pre-commit Hooks

The repository uses pre-commit hooks (`.pre-commit-config.yaml`):
- Trailing whitespace removal
- End-of-file fixing
- YAML validation
- Large file detection (max 5MB)
- Jupyter notebook output stripping (nbstripout) - keeps notebooks clean in version control

## Architecture and Code Structure

### Experimental Control Code (`src/`)

**Main Raspberry Pi experiment scripts:**
- `Final_RPE.py` - RPE experiment control (4 session types: A, H, E, R)
- `Cognitive_Bias.py` - CB experiment control (training and test sessions)

**Helper modules:**
- `experiment_helper.py` / `cb_helper.py` - Hardware setup, GPIO button initialisation, servo control (grain/pellets feeders), event logging, audio playback, parameter validation
- `experiment_sounds.py` / `cb_experiment_sounds.py` - WAV file path definitions for audio cues
- `load_experiment_design()` function in `cb_helper.py` loads trial sequences from Excel

**Key patterns in experimental control:**
1. **Hardware abstraction:** `Servo_grain`, `Servo_pellets` classes control feeders with configurable angles/delays
2. **Button-driven state machine:** 
   - Green button: starts session (1st press = ready, 2nd press = commence), releases horse for each trial
   - Red button: pauses/resumes session
   - Blue button: manual override for touch events
3. **Event logging:** All events timestamped and written to `.log` files with structured format
4. **Pausable operations:** `pausable_sleep()` function allows pause/resume during delays
5. **Audio feedback:** WAV files provide distinct cues for system states, responses, criterion achievement
6. **Session types:** Parameters workbook (`data/experiment_parameters.xlsx`) defines behaviour per session type
7. **Test mode:** Set `MODE: "test"` in parameters to reduce trial limits and timeouts for development
8. **Criterion tracking:** Automatic detection of learning criteria (consecutive correct responses within time threshold)

**Hardware requirements:**
- Raspberry Pi (tested on version 4B, 8GB RAM)
- GPIO pins for three buttons (green, blue, red)
- PiicoDev Capacitive Touch Sensor CAP1203
- DF Geared 15kg Standard Servo 270° (grain and pellets modes)
- Audio output for WAV playback (pygame)
- See `docs/hardware.md` for detailed hardware specifications and links

### Analytics Code (`src/horse_logic/`)

Core module for log file parsing and database operations:

**`logfiles.py`** - Main parsing module (950+ lines):

RPE dataclasses:
- `Experiment` - experiment metadata (ExperimentID, Cohort, SubjectName, SubjectNumber, SessionNumber, ExperimentType, Comment, DateTime, LogFileName, Parameters)
- `Trial` - trial timing (TrialID, ExperimentID, TrialNumber, TrialStartTime, TrialEndTime)
- `Event` - individual events (EventID, TrialID, EventNumber, EventTime, EventType, EventElapsedTime)

CB dataclasses:
- `ExperimentCB` - includes Direction (LEFT/RIGHT) and SessionType (training/test) at experiment level
- `TrialCB` - trial details (ResponseType: GO/NOGO, TrialSubType: P/N, CriterionType, CriterionCount)
- `ResponseCB` - GO response details (ResponseTime, EventDateTime)
- `EventCB` - all trial events with elapsed times

**`Logfile` class methods:**
- `parse_filename_components()` / `parse_filename_components_cog_bias()` - extract metadata from filename using regex
- `parse_comments()` - extract comment field from log contents
- `parse_parameters()` - extract PARAMETERS dict from log file
- Handles 'nan' session numbers and datetime parsing

**Database schema principles:**
- Hierarchical: Experiment → Trial → Event (RPE) or Experiment → Trial → (Response + Event) (CB)
- Parameters stored as JSON/dict (not normalised for flexibility)
- Timestamps in datetime format for temporal analysis
- Direction and SessionType stored at experiment level for CB (not trial level)
- See `sql/README_database_design.md` for detailed schema documentation and ERD diagrams

**Other modules:**
- `motherduck.py` - MotherDuck cloud database integration
- `project.py`, `subject.py`, `utils.py` - Supporting utilities

### Notebooks Workflow (`notebooks/`)

The analysis pipeline follows this sequence (do not deviate from order):

**1. Log file reconciliation** (determines which files to include/exclude):
- `logfile-reconciliation-RPE.ipynb`
- `logfile-reconciliation-CB.ipynb`
- **Critical output:** `data/all_files_included.csv` - specifies included/excluded files with reasons

**2. Database creation** (parse logs → DuckDB):
- `logfile-to-database-RPE.ipynb`
- `logfile-to-database-CB.ipynb`
- Outputs: `data/Experiments_{RPE|CB}_2023_Q4.ddb`
- Reads subject cohort data from `docs/from_CH/Cohort data for MB.xlsx`

**3. Database validation and queries:**
- `database-queries-RPE.ipynb` / `database-queries-CB.ipynb` - Basic exploration queries
- `database-checks-CB.ipynb` - Data validation and quality checks
- `corrections-to-database-CB.ipynb` - Identify corrections needed
- `database-apply-corrections-CB.ipynb` - Apply corrections using SQL scripts

**4. Deep-dive analysis:**
- `CSU-database-queries-CB-deep-dive.ipynb` - CSU cohort analysis
- `HD-database-queries-CB-deep-dive.ipynb` - Hillydale cohort analysis

**5. MotherDuck synchronisation:**
- `push-to-motherduck-workaround.ipynb` - Syncs local DuckDB to MotherDuck cloud platform

### Configuration

**`project_config.yaml`** - Centralised project paths:
```yaml
directories:
  data: data/  # Raw and processed data
  sql: sql/  # SQL scripts
  output:
    RPE: notebooks/results/RPE
    CB: notebooks/results/CB
  logfiles:
    RPE: data/results/zips/data_17Jan2020_email_hillydale_equine
    CB: data/results/zips/cb_data
  notebooks: notebooks/

database:
  path: data/Experiments_{experiment_type}_2023_Q4.ddb  # {experiment_type} = RPE or CB

subject:
  cohort_data:
    path: docs/from_CH/Cohort data for MB.xlsx
```

**Environment variables:**
- `.env` and `.secrets.toml` contain secrets (MotherDuck authentication tokens)
- **Never commit these files** - they are gitignored
- Use environment variables in scripts, never hardcode secrets

### SQL Scripts (`sql/`)

- `create_experiment_tables_ddb.sql` - RPE database schema
- `create_cb_experiment_tables_ddb.sql` - CB database schema  
- `corrections-to-database-CB.sql` - Manual CB data corrections
- `database-apply-corrections-CB.sql` - Automated correction application
- `ERD-CB.md` - Mermaid entity relationship diagram for CB experiments
- `README_database_design.md` - Database design rationale and initial considerations

## Key Development Considerations

### Log File Format and Parsing

**Filename naming conventions:**
- RPE: `{suffix}_{datetime}_{subject_name}_{session_number}_{experiment_type}.log`
  - Example: `Experiment_2023-05-10T14:30:00.123456_Apollo_3_RPE-A.log`
- CB: `Experiment_{datetime}_{subject_name}_{session_number}_{experiment_type}.log`
  - Example: `Experiment_2023-10-09T17:45:46.540359_apollo_5_Training randomised Type 1.log`

**Log file structure (sequential):**
1. PARAMETERS block - Python dict with experiment configuration (all caps keys)
2. Metadata lines - Comment, Data directory, Log file, Measurement file
3. Trial/Event sequences - timestamped events with structured format

**Parsing considerations:**
- `Logfile` class handles all parsing in `src/horse_logic/logfiles.py`
- Session numbers may be 'nan' (converted to None in Python)
- Datetimes in ISO format with microseconds
- Parameters dict contains mixed types (str, int, float, bool)
- See `docs/CB-logfile-example-parsing.md` for detailed CB parsing example

### Raspberry Pi Hardware Integration

**Hardware control patterns:**
- GPIO pins configured via `initialise_GPIO_buttons()` function
- Touch sensor interface via PiicoDev library (I2C communication)
- Servo motors controlled with angle/duration parameters (grain vs pellets have different configurations)
- Audio playback via pygame mixer (mono WAV files)

**Graceful degradation:**
- Hardware-specific code checks for Raspberry Pi environment
- Test mode available for local development (sets `touchSensor = None`)
- Scripts exit gracefully when hardware unavailable

**Session data files:**
- Log files (`.log`) contain all events with timestamps
- Quantity files (`.csv`) track feed dispensing (RPE only)
- Measurement files (`.csv`) track additional metrics (CB only)

### Database Patterns

**Technology choices:**
- **DuckDB** for local analysis - OLAP-optimised, embedded, supports complex analytical queries
- **MotherDuck** for cloud collaboration - managed DuckDB service with sharing capabilities
- No traditional RDBMS (PostgreSQL/MySQL) - prioritising analytical performance over transactional integrity

**Schema patterns:**
- Parameters as JSON/dict columns (flexible, self-documenting from log files)
- Datetime columns for temporal analysis (not Unix timestamps)
- Auto-incrementing integer primary keys
- Foreign key relationships enforced via naming (ExperimentID, TrialID)

**Data loading patterns:**
- Bulk insert from pandas DataFrames
- Subject cohort data joined from external Excel file
- Corrections applied via SQL UPDATE statements after initial load

### Testing and Validation

**Current state:**
- No formal test suite exists
- Experimental scripts have built-in "test mode"
- Database validation via SQL queries in notebooks
- Manual verification against expected patterns

**Test mode usage:**
```python
# In experiment parameters workbook:
MODE: "test"  # Reduces trial limits, timeouts for rapid iteration
```

**When making changes:**
1. Test experimental scripts in test mode first
2. Validate database outputs against known-good log files
3. Run pre-commit hooks before committing
4. Check notebook outputs render correctly via `just render`

### Publishing and Collaboration

**Quarto publishing workflow:**
- Notebooks rendered to HTML using Quarto
- Published to separate public repo: `https://github.com/DataBooth/horselogic-nb-publish.git`
- Command: `just publish` renders + pushes to `gh-pages` branch
- Published site serves as shareable analysis documentation

**MotherDuck sharing:**
- Local DuckDB databases synced to MotherDuck for collaboration
- Researchers can query cloud databases without local setup
- Use `just cp2md local_db remote_db` for sync

### Common Development Tasks

**Adding a new parameter to experiments:**
1. Update `data/experiment_parameters.xlsx` with parameter name, value, units, validation range
2. Reference parameter in experimental control code via `p["PARAMETER_NAME"]`
3. Parameter automatically logged to log files
4. No code changes needed for database ingestion (parameters stored as dict)

**Processing a new batch of experiments:**
1. Place log files in appropriate directory (`data/results/zips/...`)
2. Run reconciliation notebook to determine included files
3. Run database creation notebook to parse and load
4. Run validation notebooks to verify data quality
5. Sync to MotherDuck if collaboration needed

**Modifying database schema:**
1. Update SQL schema files in `sql/` directory
2. Update dataclasses in `src/horse_logic/logfiles.py`
3. Update parsing logic if log file format changed
4. Document changes in ERD diagrams
5. Create migration script if existing databases need updating

**Creating new analysis notebook:**
1. Place in `notebooks/` directory
2. Follow naming convention: `{purpose}-{experiment_type}.ipynb`
3. Load database using pattern from existing notebooks
4. Use DuckDB SQL for analysis queries
5. Strip outputs before committing (pre-commit hook does this)
6. Optionally add to Quarto publishing workflow
