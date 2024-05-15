# https://just.systems/

# import './docker.just'

default:
  @just --list

reqs:
    pdm export --o requirements.txt --without-hashes --prod

quarto notebook="notebooks/logfile-data-extraction.ipynb":
    quarto render {{notebook}} --execute

zip-quarto notebook="logfile-data-extraction":
    zip -r analysis.zip notebooks/{{notebook}}.html notebooks/{{notebook}}_files/ data/results/notebooks/all_excluded_files.csv data/results/notebooks/included_files.csv data/results/notebooks/bonnie_excluded_files.csv  data/results/notebooks/experiment_summary_Oct2023_included.csv


update-st-config:
    streamlit config show > .streamlit/config.toml

app app_name="":
    streamlit run {{app_name}} --server.address=localhost

# View/edit DuckDB database with Harlequin CLI (optional db_name)
duck db_name="":
    harlequin --theme github-dark {{db_name}}

pre-commit_update:
    pre-commit autoupdate

pre-commit_test:
    pre-commit run --all-files

zip-report report_html:
    #!/usr/bin/env bash
    zip -er report.zip {{report_html}}
