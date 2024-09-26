## High Level Summary of Experimental Data Analysis

The Jupyter notebooks and supporting Python code are part of a data analysis pipeline for horse behavioural experiments.

The primary goal is to process and analyse log files generated during these experiments, specifically focusing on Reward Prediction Error (RPE) experiments. This data is loaded in to a DuckDB database which provides a familiar and easy to use SQL engine to query the conformed data. An analogous set of notebooks and code are available for the Cognitive Bias experiments (note that this are yet to be finalised).

High-level summary of the analysis and data manipulations:

1. Logfile Reconciliation (`logfile-reconciliation-RPE.ipynb`):

- Purpose: This notebook identifies which log files should be included or excluded from the analysis.
- Steps:
  - Load and Parse Log Files: Load log files from a specified directory and parse their filenames to extract metadata (e.g., subject name, experiment type).
  - Apply Exclusion Rules: Exclude log files based on predefined rules (e.g., test runs, bad data).
  - Handle Specific Files: Include or exclude specific log files based on additional criteria.
  - Export Lists: Export lists of included and excluded log files for further processing.

2. Logfile to Database (`logfile-to-database-RPE.ipynb`):

- Purpose: This notebook loads the reconciled log files into a DuckDB database for detailed analysis.
- Steps:
  - Load Log Files: Load the log files determined to be included from the reconciliation step.
  - Parse and Extract Data: Extract relevant data from each log file (e.g., events, trials) and structure it for database insertion.
  - Insert Data into Database: Insert the parsed data into a DuckDB database.
  - Export Database Tables: Export the database tables to human-readable formats (e.g., Excel, CSV) for review.

3. Supporting Code (`logfiles.py`):

- Classes and Functions:
  - Logfile Class: Handles the loading and parsing of individual log files.
  - Logs Class: Manages a collection of log files, applies exclusion rules, and creates dataframes for analysis.
  - Data Classes: Define the structure of experiments, trials, and events for both RPE and Cognitive Bias (CB) experiments.
  - Utility Functions: Provide additional functionality such as exporting data to CSV and displaying session summaries.

### Workflow Diagram

Below is a diagram summarising the data workflow:

```{mermaid}
graph TD
    A[Start] --> B[Load Log Files]
    B --> C[Parse Filenames]
    C --> D[Apply Exclusion Rules]
    D --> E[Handle Specific Files]
    E --> F[Export Included/Excluded Lists]
    F --> G[Load Included Log Files]
    G --> H[Parse and Extract Data]
    H --> I[Insert Data into DuckDB]
    I --> J[Export Database Tables]
    J --> K[End]

    classDef process fill:#f9f,stroke:#333,stroke-width:2px;
    class A,B,C,D,E,F,G,H,I,J,K process;
```

### Explanation of the Diagram

1. Start: The process begins with the loading of log files.
2. Load Log Files: Log files are loaded from a specified directory.
3. Parse Filenames: Filenames are parsed to extract metadata such as subject name and experiment type.
4. Apply Exclusion Rules: Predefined rules are applied to exclude certain log files.
5. Handle Specific Files: Additional criteria are used to include or exclude specific log files.
6. Export Included/Excluded Lists: Lists of included and excluded log files are exported for further processing.
7. Load Included Log Files: The included log files are loaded for detailed analysis.
8. Parse and Extract Data: Relevant data is extracted from each log file and structured for database insertion.
9. Insert Data into DuckDB: The parsed data is inserted into a DuckDB database.
10. Export Database Tables: The database tables are exported to human-readable formats for review.
11. End: The process concludes with the export of database tables.

This workflow ensures that only relevant and high-quality (and non-testing) log files are included in the analysis, and the data is structured and stored in a database for further analysis and review.
