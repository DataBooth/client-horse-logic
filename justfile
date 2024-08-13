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

# Export Jupyter notebook to Python and run it, optionally capturing output
run-notebook notebook keep_py="false" capture_output="false":
    #!/usr/bin/env bash
    set -euo pipefail

    notebook_abs_path=$(realpath "{{notebook}}")
    notebook_dir=$(dirname "$notebook_abs_path")
    notebook_name=$(basename "$notebook_abs_path")
    base_name=$(basename "$notebook_abs_path" .ipynb)

    echo "Converting {{notebook}} to Python script..."
    jupyter nbconvert --to python "$notebook_abs_path" --TemplateExporter.exclude_raw=True --no-prompt

    echo "Running ${notebook_dir}/${base_name}.py..."
    if [ "{{capture_output}}" = "true" ]; then
        output_file="${notebook_dir}/${base_name}_output.txt"
        (cd "$notebook_dir" && python "${base_name}.py") 2>&1 | tee "$output_file"
        echo "Output captured in $output_file"
    else
        (cd "$notebook_dir" && python "${base_name}.py")
    fi

    if [ "{{keep_py}}" != "true" ]; then
        echo "Removing ${notebook_dir}/${base_name}.py"
        rm "${notebook_dir}/${base_name}.py"
    else
        echo "Keeping ${notebook_dir}/${base_name}.py"
    fi

# Run two notebooks in sequence with options to keep .py files and capture output
run-notebooks notebook1="notebooks/logfile-reconciliation-RPE.ipynb" notebook2="notebooks/logfile-reconciliation-CB.ipynb" keep_py="false" capture_output="false":
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Running first notebook: {{notebook1}}"
    just run-notebook {{notebook1}} {{keep_py}} {{capture_output}}

    echo "Running second notebook: {{notebook2}}"
    just run-notebook {{notebook2}} {{keep_py}} {{capture_output}}

    echo "Notebook execution complete."
    if [ "{{keep_py}}" = "true" ]; then
        echo ".py files have been retained."
    else
        echo ".py files have been removed."
    fi
    if [ "{{capture_output}}" = "true" ]; then
        echo "Output has been captured for each notebook."
    fi
