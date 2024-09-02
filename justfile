# https://just.systems/

# Default output directory for PDF/HTML documents created from markdown
default_output_dir := "docs/output"


# List all just recipes
default:
  @just --list

# Export requirements.txt from pyproject.toml using PDM
reqs:
    pdm export --o requirements.txt --without-hashes --prod

# Execute and render a Quarto notebook (to .html)
quarto notebook="notebooks/logfile-reconciliation-RPE.ipynb" quarto_render_dir="quarto_output":
    #!/usr/bin/env bash
    set -euo pipefail

    notebook_abs_path=$(realpath "{{notebook}}")
    notebook_dir=$(dirname "$notebook_abs_path")
    output_dir=$(realpath "${notebook_dir}/{{quarto_render_dir}}")
    notebook_name=$(basename "{{notebook}}")

    # Ensure the output directory exists
    mkdir -p "$output_dir"

    # Change to the notebook directory before rendering
    cd "$notebook_dir"

    # Render the notebook
    quarto render "$notebook_name" --execute --output-dir "$output_dir"

    echo "Rendered $notebook_name to $output_dir"

# Package up the .html version of the notebook and supporting files
zip-quarto notebook="notebooks/logfile-reconciliation-RPE.ipynb" output_zip="analysis.zip":
    #!/usr/bin/env bash
    set -euo pipefail

    # Extract the base name without extension
    base_name=$(basename "{{notebook}}" .ipynb)
    dir_name=$(dirname "{{notebook}}")

    # Check if the HTML file exists
    if [ ! -f "${dir_name}/${base_name}.html" ]; then
        echo "Error: ${dir_name}/${base_name}.html not found. Make sure the notebook has been rendered to HTML."
        exit 1
    fi

    # Check if the supporting files directory exists
    if [ ! -d "${dir_name}/${base_name}_files" ]; then
        echo "Error: ${dir_name}/${base_name}_files directory not found. Supporting files are required."
        exit 1
    fi

    # Create the ZIP file
    zip -r "{{output_zip}}" "${dir_name}/${base_name}.html" "${dir_name}/${base_name}_files"

    echo "Created {{output_zip}} with ${base_name}.html and supporting files."

# Compress the report .html
zip-report report_html:
    #!/usr/bin/env bash
    zip -er report.zip {{report_html}}

# Create/update the project directory tree structure in markdown
dir-md outfile="docs/complete_directory_structure.md":
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


# Check if pandoc is installed
check-pandoc:
    #!/usr/bin/env bash
    if ! command -v pandoc &> /dev/null; then
        echo "Error: Pandoc is not installed. Please install pandoc to proceed."
        exit 1
    fi

# Match files and display them
match-files md_pattern:
    #!/usr/bin/env bash
    set -euo pipefail
    shopt -s nullglob
    matched_files=({{md_pattern}})
    shopt -u nullglob
    if [ ${#matched_files[@]} -eq 0 ]; then
        echo "No files matched the pattern: {{md_pattern}}"
        exit 0
    fi
    echo "Files to be converted:"
    for file in "${matched_files[@]}"; do
        echo "  $(pwd)/$file"
    done

# Ask for user confirmation
confirm-action:
    #!/usr/bin/env bash
    read -p "Proceed with conversion? [Y/n] " -n 1 -r user_input
    echo
    if [[ ! $user_input =~ ^[Yy]?$ ]]; then
        echo "Conversion cancelled by user."
        exit 0
    fi

# Convert markdown to PDF
convert-to-pdf file output_file:
    pandoc "{{file}}" -o "{{output_file}}" \
        --pdf-engine=xelatex \
        -V mainfont="DejaVu Sans" \
        -V monofont="DejaVu Sans Mono" \
        --highlight-style=tango

# Convert markdown to HTML
convert-to-html file output_file:
    pandoc "{{file}}" -o "{{output_file}}" \
        -s --toc --toc-depth=2 \
        --highlight-style=tango \
        -c https://cdn.jsdelivr.net/npm/water.css@2/out/water.css

convert-md md_pattern="docs/*.md" output_dir="docs/output" format="pdf":
    #!/usr/bin/env bash
    set -euo pipefail

    # Validate format
    if [[ "{{format}}" != "pdf" && "{{format}}" != "html" ]]; then
        echo "Error: Invalid format. Use 'pdf' or 'html'."
        exit 1
    fi

    just match-files "{{md_pattern}}"

    full_output_dir="$(pwd)/{{output_dir}}"
    echo "Output directory: $full_output_dir"
    echo "Output format: {{format}}"

    just confirm-action

    # Ensure the output directory exists
    mkdir -p "$full_output_dir"

    for file in {{md_pattern}}; do
        if [ -f "$file" ]; then
            output_file="$full_output_dir/$(basename "${file%.md}.{{format}}")"
            echo "Converting $file to $output_file"

            if [ "{{format}}" = "pdf" ]; then
                just convert-to-pdf "$file" "$output_file" || echo "Warning: Failed to convert $file to PDF. Skipping."
            else
                just convert-to-html "$file" "$output_file" || echo "Warning: Failed to convert $file to HTML. Skipping."
            fi
        else
            echo "Warning: $file not found or not a regular file. Skipping."
        fi
    done

    echo "Conversion complete. Output files are in $full_output_dir"



# Show the values of the arguments
# Show the values of the arguments
show_args md_pattern="docs/*.md" output_dir="docs/output" format="pdf":
    #!/usr/bin/env bash
    echo "Argument values:"
    echo "  md_pattern: {{md_pattern}}"
    echo "  output_dir: {{output_dir}}"
    echo "  format: {{format}}"
