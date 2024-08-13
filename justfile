# https://just.systems/

default:
  @just --list

reqs:
    pdm export --o requirements.txt --without-hashes --prod

quarto notebook="notebooks/logfile-reconciliation-RPE.ipynb":
    quarto render {{notebook}} --execute

zip-quarto notebook="notebooks/logfile-reconciliation-RPE":
    zip -r analysis.zip {{notebook}}.html {{notebook}}_files/ data/results/notebooks/cb/*.csv

zip-report report_html:
    #!/usr/bin/env bash
    zip -er report.zip {{report_html}}

dir-report outfile="docs/complete_directory_structure.md":
    echo '```' > {{outfile}}
    tree --noreport --gitignore -I '__pycache__|*.csv|*.log' >> {{outfile}}
    echo '```' >> {{outfile}}

# Export Jupyter notebook to Python and run it
run-notebook notebook:
    #!/usr/bin/env bash
    set -euo pipefail

    # Extract directory and filename
    notebook_dir=$(dirname "{{notebook}}")
    notebook_name=$(basename "{{notebook}}")

    echo "Converting {{notebook}} to Python script..."
    jupyter nbconvert --to python "{{notebook}}" --TemplateExporter.exclude_raw=True

    # Extract the base name without extension
    base_name=$(basename "{{notebook}}" .ipynb)

    echo "Running ${notebook_dir}/${base_name}.py..."
    python "${notebook_dir}/${base_name}.py"
