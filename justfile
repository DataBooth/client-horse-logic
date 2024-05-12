# https://just.systems/

# import './docker.just'

default:
  @just --list

reqs:
    pdm export --o requirements.txt --without-hashes --prod

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
