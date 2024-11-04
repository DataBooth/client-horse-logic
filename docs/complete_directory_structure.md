```
.
├── README.md
├── data
│   └── results
│       ├── CB
│       ├── RPE
│       └── zips
│           ├── cb_data
│           └── data_17Jan2020_email_hillydale_equine
├── docs
│   ├── CB-logfile-example-parsing.md
│   ├── ERD_cog_bias.ipynb
│   ├── README_Python_setup.md
│   ├── README_data_logging.md
│   ├── README_experiment.md
│   ├── README_experiment_types.md
│   ├── background_info.md
│   ├── complete_directory_structure.md
│   ├── experiment_directory_structure.md
│   ├── from_CH
│   │   ├── 1Button_manual_testcode.py
│   │   ├── 2Final_RPE_code_DRAFT.py
│   │   ├── 2Final_RPE_code_DRAFT1.py
│   │   ├── 4RPE_timelog_sequence_tones.py
│   │   ├── 4buzzer_touch2_counts_touchonly_servo.py
│   │   ├── 5RPE_timelog_sequence_tones_datalog.py
│   │   ├── 8buzzer_testcode_with_delay_timelog.py
│   │   ├── CB horse Bucket sides CSU.docx
│   │   ├── CB horse Bucket sides HD.docx
│   │   ├── ChatGPT advice-code for squence.docx
│   │   ├── Code
│   │   │   ├── OldCode
│   │   │   │   ├── 1Big_button_as_object.py
│   │   │   │   ├── 1Final_RPE_code_DRAFT.py
│   │   │   │   ├── 1button_4RPE_sequence_tones_USE.py
│   │   │   │   ├── 2Big_buttons_2_for_manual__operation.py
│   │   │   │   ├── 2Final_RPE_code_DRAFT.py
│   │   │   │   ├── 3Final_RPE_code_DRAFT.py
│   │   │   │   ├── 4RPE_timelog_sequence_tones_USE.py
│   │   │   │   └── 5RPE_timelog_sequence_tones_USE.py
│   │   │   ├── data
│   │   │   └── src
│   │   ├── Criterion variables.docx
│   │   ├── Data logging flow.docx
│   │   ├── Example data sheets output from Excel.pdf
│   │   ├── Exp design-RPi doc.docx
│   │   ├── OCR
│   │   │   ├── Exp2TimingSheets day 1 - FirstPage.pdf
│   │   │   ├── Exp2TimingSheets day 1 Pages1-2.pdf
│   │   │   ├── Exp2TimingSheets day 1.pdf
│   │   │   ├── Exp2TimingSheets day 1.txt
│   │   │   ├── Exp2TimingSheets day 6.pdf
│   │   │   ├── FirstPage_SemiAutoParse.pdf
│   │   │   └── example_pred_exp_worksheet.txt
│   │   ├── email_14Aug2023.md
│   │   ├── experimental_apparatus.png
│   │   ├── experimental_controller.png
│   │   ├── simple_button_10.py
│   │   └── wagga
│   │       ├── Exp method for Wagga.docx
│   │       └── Exp method for Wagga.md
│   ├── hardware.md
│   ├── high_level_data_analysis_diagram.ipynb
│   ├── images
│   │   ├── Whiteboard_14July2023_Page1.jpeg
│   │   └── Whiteboard_14July2023_Page2.jpeg
│   ├── method_paper.docx
│   ├── method_paper.md
│   ├── output
│   └── pdf_output
├── justfile
├── justfile.tmp
├── notebooks
│   ├── CSU-database-queries-CB-deep-dive.ipynb
│   ├── HD-database-queries-CB-deep-dive.ipynb
│   ├── OCR-tests
│   │   ├── pred-exp-worksheet-initial-parse.ipynb
│   │   └── try-tesseract-ocr.ipynb
│   ├── _quarto.yml
│   ├── about.qmd
│   ├── archive-analysis
│   │   ├── create-duckdb-sql.ipynb
│   │   ├── data-table-xl-test.ipynb
│   │   ├── experimental_parameters.ipynb
│   │   ├── explore-oct2023-duckdb.ipynb
│   │   ├── logfile-cb-errors.ipynb
│   │   ├── motherduck-class.ipynb
│   │   ├── motherduck.ipynb
│   │   ├── rpe-initial-analysis.ipynb
│   │   ├── testing-log-parameters.ipynb
│   │   ├── testing_experiment_subjects.ipynb
│   │   ├── testing_experiment_tracking.ipynb
│   │   ├── try-create-duckdb-orm.ipynb
│   │   └── upload-to-motherduck.ipynb
│   ├── archive-experiment
│   │   ├── analyse_sensor_data.ipynb
│   │   ├── base_experiment_testing.ipynb
│   │   ├── read-in-experiment-schedule.ipynb
│   │   ├── simulate_senor_data.ipynb
│   │   ├── simulate_trials.ipynb
│   │   ├── test-read-schedule.ipynb
│   │   ├── text-to-speech.ipynb
│   │   └── verify_dataclass_definitions.ipynb
│   ├── background
│   │   └── analyse-sample-results.ipynb
│   ├── corrections-to-database-CB.ipynb
│   ├── database-checks-CB.ipynb
│   ├── database-queries-CB.ipynb
│   ├── database-queries-RPE.ipynb
│   ├── index.qmd
│   ├── logfile-reconciliation-CB.ipynb
│   ├── logfile-reconciliation-RPE.ipynb
│   ├── logfile-to-database-CB.ipynb
│   ├── logfile-to-database-RPE.ipynb
│   ├── notebook_helper.py
│   ├── parse
│   ├── push-to-motherduck-workaround.ipynb
│   └── results
│       ├── CB
│       │   └── export_tables
│       └── RPE
│           └── export_tables
├── output
├── pdm.lock
├── project_config.yaml
├── pyproject.toml
├── requirements.txt
├── sql
│   ├── README_database_design.md
│   ├── check_insert.sql
│   ├── correction-table-views.sql
│   ├── create_cb_experiment_tables_ddb.sql
│   ├── create_experiment_tables_ddb.sql
│   ├── erd.mermaid
│   ├── example_insert.sql
│   └── reconstruct_log_filename_example.sql
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
    │   ├── database_INPROGRESS.py
    │   ├── logfiles.py
    │   ├── logfiles_README.md
    │   ├── logfiles_refactored_example_only.py
    │   ├── motherduck.py
    │   ├── project.py
    │   ├── subject.py
    │   ├── utils.py
    │   └── utils_README.md
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
