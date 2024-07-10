```
.
├── README.md
├── README_Python_setup.md
├── data
│   └── results
│       ├── CB
│       ├── RPE
│       │   └── export_tables
│       └── zips
│           ├── cb_data
│           └── data_17Jan2020_email_hillydale_equine
├── docs
│   ├── README_data_logging.md
│   ├── README_experiment.md
│   ├── README_experiment_types.md
│   ├── Whiteboard_14July2023_Page1.jpeg
│   ├── Whiteboard_14July2023_Page2.jpeg
│   ├── background_info.md
│   ├── complete_directory_structure.md
│   ├── experiment_directory_structure.md
│   ├── hardware.md
│   └── provided
│       ├── 1Button_manual_testcode.py
│       ├── 2Final_RPE_code_DRAFT.py
│       ├── 2Final_RPE_code_DRAFT1.py
│       ├── 4RPE_timelog_sequence_tones.py
│       ├── 4buzzer_touch2_counts_touchonly_servo.py
│       ├── 5RPE_timelog_sequence_tones_datalog.py
│       ├── 8buzzer_testcode_with_delay_timelog.py
│       ├── CB horse Bucket sides CSU.docx
│       ├── CB horse Bucket sides HD.docx
│       ├── ChatGPT advice-code for squence.docx
│       ├── Code
│       │   ├── OldCode
│       │   │   ├── 1Big_button_as_object.py
│       │   │   ├── 1Final_RPE_code_DRAFT.py
│       │   │   ├── 1button_4RPE_sequence_tones_USE.py
│       │   │   ├── 2Big_buttons_2_for_manual__operation.py
│       │   │   ├── 2Final_RPE_code_DRAFT.py
│       │   │   ├── 3Final_RPE_code_DRAFT.py
│       │   │   ├── 4RPE_timelog_sequence_tones_USE.py
│       │   │   └── 5RPE_timelog_sequence_tones_USE.py
│       │   ├── data
│       │   └── src
│       ├── Criterion variables.docx
│       ├── Data logging flow.docx
│       ├── Example data sheets output from Excel.pdf
│       ├── Exp design-RPi doc.docx
│       ├── OCR
│       │   ├── Exp2TimingSheets day 1 - FirstPage.pdf
│       │   ├── Exp2TimingSheets day 1 Pages1-2.pdf
│       │   ├── Exp2TimingSheets day 1.pdf
│       │   ├── Exp2TimingSheets day 1.txt
│       │   ├── Exp2TimingSheets day 6.pdf
│       │   ├── FirstPage_SemiAutoParse.pdf
│       │   └── example_pred_exp_worksheet.txt
│       ├── email_14Aug2023.md
│       ├── experimental_apparatus.png
│       ├── experimental_controller.png
│       ├── simple_button_10.py
│       └── wagga
│           ├── Exp method for Wagga.docx
│           └── Exp method for Wagga.md
├── justfile
├── notebooks
│   ├── analyse-sample-results.ipynb
│   ├── analyse_sensor_data.ipynb
│   ├── base_experiment_testing.ipynb
│   ├── create-duckdb-sql.ipynb
│   ├── data-table-xl-test.ipynb
│   ├── database-queries.ipynb
│   ├── experimental_parameters.ipynb
│   ├── explore-oct2023-duckdb.ipynb
│   ├── logfile-cb-errors.ipynb
│   ├── logfile-reconciliation-cb.ipynb
│   ├── logfile-reconciliation.ipynb
│   ├── logfile-to-database-cb.ipynb
│   ├── logfile-to-database.ipynb
│   ├── logfile_data_extraction_README.md
│   ├── motherduck-class.ipynb
│   ├── motherduck-simple.ipynb
│   ├── motherduck.ipynb
│   ├── notebook_helper.py
│   ├── parse
│   ├── pred-exp-worksheet-initial-parse.ipynb
│   ├── read-in-experiment-schedule.ipynb
│   ├── rpe-initial-analysis.ipynb
│   ├── simulate_senor_data.ipynb
│   ├── simulate_trials.ipynb
│   ├── test-read-schedule.ipynb
│   ├── testing-log-parameters.ipynb
│   ├── testing_experiment_subjects.ipynb
│   ├── testing_experiment_tracking.ipynb
│   ├── text-to-speech.ipynb
│   ├── try-create-duckdb-orm.ipynb
│   ├── try-tesseract-ocr.ipynb
│   └── verify_dataclass_definitions.ipynb
├── pdm.lock
├── pyproject.toml
├── requirements.txt
├── sql
│   ├── README_database_design.md
│   ├── check_insert.sql
│   ├── create_experiment_tables_ddb.sql
│   ├── erd.mermaid
│   ├── example_insert.sql
│   └── reconstruct_log_filename_test.sql
└── src
    ├── Cognitive_Bias.py
    ├── Final_RPE.py
    ├── archive
    │   ├── 4RPE_timelog_sequence_tones_datalog.py
    │   ├── base_experiment.py
    │   ├── experiment.py
    │   └── hardware.py
    ├── cb_experiment_sounds.py
    ├── cb_helper.py
    ├── experiment_helper.py
    ├── experiment_sounds.py
    ├── horse_logic
    │   ├── __init__.py
    │   ├── logfiles.py
    │   ├── logfiles_README.md
    │   ├── motherduck.py
    │   └── utils.py
    ├── oo-approach
    │   ├── config.py
    │   ├── config.toml
    │   ├── data_manager.py
    │   ├── experiment.py
    │   ├── experiment_helper.py
    │   ├── experiment_sounds.toml
    │   ├── main.py
    │   ├── sound_manager.py
    │   └── tests
    │       └── test_experiment.py
    ├── phase2
    │   ├── Experiment.py
    │   ├── Experiment_functional_TODELETE.py
    │   ├── README.md
    │   ├── config.toml
    │   ├── control.py
    │   ├── data_table_xl.py
    │   ├── equipment.py
    │   ├── experiment_helper.py
    │   ├── install_python_dependencies.sh
    │   ├── logger.py
    │   ├── requirements.txt
    │   ├── show_python_info.py
    │   └── text_to_speech.py
    ├── scripts
    │   ├── csv
    │   ├── example_logfiles.py
    │   ├── example_parse_log.py
    │   ├── load_execute_dot_sql.py
    │   └── logs_to_duckdb.py
    └── tones
        ├── Correct_tone_1000.wav
        ├── End_tone_1200.wav
        └── Start_tone_600.wav
```
