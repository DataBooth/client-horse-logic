# `horse-logic`

This repository contains code for behavioural experiments conducted with horses at Charles Sturt University (Wagga Wagga, NSW). The project has two main components:

1. **Experimental control code** - Python scripts that run on Raspberry Pi hardware to control experiments, capture sensor data, and log horse responses to stimuli
2. **Analytics pipeline** - Jupyter notebooks that parse experimental log files, load data into DuckDB databases, and enable SQL-based analysis

## Experiment Types

### RPE (Response to Positive Expectation)

Measures horse latency responses to various stimuli across four session types:

- **RPE-A (Acquisition)** - horses learn to respond to start tone by touching panel
- **RPE-H (Habit)** - habitual responding develops (fixed 20 trials × 3 sessions)
- **RPE-E (Extinction)** - response extinguished without food rewards
- **RPE-R (Reinstatement)** - touch response reinstated

### CB (Cognitive Bias)

Evaluates horse decision-making patterns with training and test sessions:

- Training sessions: fixed block (positive LEFT/RIGHT), randomised Type 1 & 2
- Test sessions: Type 1, 2, 3
- Trials use positive/negative/median/near-positive/near-negative stimuli

## Development Environment

### Dependencies

The project uses **uv** for Python dependency management. Dependencies are defined in `pyproject.toml` (requires Python >= 3.10).

Key dependency groups:
- Production: pandas, DuckDB, matplotlib, loguru, pygame, seaborn, python-dotenv
- `dev` - Jupyter notebooks, black formatter, pre-commit hooks
- `hardware` - Raspberry Pi-specific packages (pigpio, piicodev)

### Task Automation

The project uses **just** for task automation. Common commands:

```bash
# Notebook execution
just run-notebooks  # Runs both RPE and CB reconciliation notebooks

# Quarto rendering
just render         # Render all notebooks
just publish        # Render and publish to GitHub Pages

# Documentation
just convert-md "docs/*.md" docs/output pdf  # Convert markdown to PDF
just dir-md         # Generate directory tree markdown
```

## Experimental Control Code

### Main Scripts

- `src/Final_RPE.py` - RPE experiment control (4 session types: A, H, E, R)
- `src/Cognitive_Bias.py` - CB experiment control (training and test sessions)

### Helper Modules

- `src/experiment_helper.py` / `src/cb_helper.py` - Hardware setup, GPIO control, servo feeders, event logging
- `src/experiment_sounds.py` / `src/cb_experiment_sounds.py` - Audio cue definitions

### Hardware Requirements

- Raspberry Pi (tested on version 4B, 8GB RAM)
- GPIO pins for three buttons (green, blue, red)
- PiicoDev Capacitive Touch Sensor CAP1203
- DF Geared 15kg Standard Servo 270° (grain and pellets modes)
- Audio output for WAV playback

See `docs/hardware.md` for detailed specifications.

## Analytics Pipeline

The analysis workflow follows this sequence:

### 1. Log File Reconciliation

Determine which log files to include/exclude:

- `notebooks/logfile-reconciliation-RPE.ipynb`
- `notebooks/logfile-reconciliation-CB.ipynb`

**Output:** `data/all_files_included.csv`

### 2. Database Creation

Parse log files and create DuckDB databases:

- `notebooks/logfile-to-database-RPE.ipynb`
- `notebooks/logfile-to-database-CB.ipynb`

**Output:** `data/Experiments_{RPE|CB}_2023_Q4.ddb`

### 3. Database Validation and Queries

- `notebooks/database-queries-RPE.ipynb` / `notebooks/database-queries-CB.ipynb` - Basic exploration
- `notebooks/database-checks-CB.ipynb` - Data validation
- `notebooks/corrections-to-database-CB.ipynb` - Identify corrections
- `notebooks/database-apply-corrections-CB.ipynb` - Apply corrections

### 4. Deep-Dive Analysis

- `notebooks/CSU-database-queries-CB-deep-dive.ipynb` - CSU cohort analysis
- `notebooks/HD-database-queries-CB-deep-dive.ipynb` - Hillydale cohort analysis

## Key Modules

### `src/horse_logic/logfiles.py`

Main parsing module with dataclasses for:

**RPE:**
- `Experiment` - experiment metadata
- `Trial` - trial timing
- `Event` - individual events

**CB:**
- `ExperimentCB` - includes Direction and SessionType
- `TrialCB` - trial details with ResponseType
- `ResponseCB` - GO response details
- `EventCB` - all trial events

### Other Modules

- `src/horse_logic/project.py`, `subject.py`, `utils.py` - Supporting utilities

## Configuration

Project paths are centralised in `project_config.yaml`. Environment variables and secrets are stored in `.env` and `.secrets.toml` (gitignored).

## Database Schema

- Hierarchical structure: Experiment → Trial → Event (RPE) or Experiment → Trial → (Response + Event) (CB)
- Parameters stored as JSON/dict for flexibility
- Timestamps in datetime format
- See `sql/README_database_design.md` and `sql/ERD-CB.md` for detailed documentation

## Pre-commit Hooks

The repository uses pre-commit hooks for:
- Trailing whitespace removal
- YAML validation
- Large file detection (max 5MB)
- Jupyter notebook output stripping (nbstripout)

## Documentation

See `WARP.md` for comprehensive development guidance including detailed architecture, patterns, and common development tasks.

---

## Appendix: MotherDuck Integration (Optional)

The project includes optional support for [MotherDuck](https://motherduck.com), a cloud-based DuckDB platform, though in practice database files are typically shared directly.

### MotherDuck Commands

```bash
just cp2md local_db remote_db  # Copy local DuckDB to MotherDuck cloud
```

### Related Files

- `src/horse_logic/motherduck.py` - MotherDuck cloud integration
- `notebooks/push-to-motherduck-workaround.ipynb` - Sync notebook
