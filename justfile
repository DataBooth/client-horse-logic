# https://just.systems/

default:
  @just --list

reqs:
    pdm export --o requirements.txt --without-hashes --prod

quarto notebook="notebooks/logfile-data-extraction.ipynb":
    quarto render {{notebook}} --execute

zip-quarto notebook="logfile-data-extraction":
    zip -r analysis.zip notebooks/{{notebook}}.html notebooks/{{notebook}}_files/ data/results/notebooks/cb/*.csv

zip-report report_html:
    #!/usr/bin/env bash
    zip -er report.zip {{report_html}}

dir-report outfile="docs/complete_directory_structure.md":
    echo '```' > {{outfile}}
    tree --noreport --gitignore -I '__pycache__|*.csv|*.log' >> {{outfile}}
    echo '```' >> {{outfile}}
