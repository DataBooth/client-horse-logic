import sys
from pathlib import Path
import datetime as dt
from IPython.display import display, Markdown
import logging

# Check if we are in a Jupyter notebook environment
if 'ipykernel' in sys.modules and hasattr(sys.stdout, 'isatty') and not sys.stdout.isatty():
    # We are in a Jupyter notebook
    logging_stream = sys.stdout
    print("Logging output redirected to Jupyter notebook")
else:
    # Not in a Jupyter notebook, or we are in an environment like IPython terminal
    logging_stream = None  # Default stream that logs to stderr

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", stream=logging_stream)

def notebook_add_parent_dir_to_path():
    """
    Adds the parent directory of the current working directory to the PYTHONPATH if it is not already included.

    Example Usage:
    notebook_add_parent_dir_to_path()

    Inputs:
    None

    Flow:
    1. Get the parent directory of the current working directory.
    2. Check if the parent directory is already in the PYTHONPATH.
    3. If not, add the parent directory to the PYTHONPATH.
    4. Display an information message indicating that the parent directory has been added to the PYTHONPATH.

    Outputs:
    None
    """
    module_path = Path.cwd().parent.as_posix()
    if module_path not in sys.path:
        sys.path.append(module_path)
        disp_md(f"INFO: Added parent directory {module_path} to PYTHONPATH")


def start_execution_time():
    start_time = dt.datetime.now()
    disp_md(f"INFO: Notebook execution start time: {start_time.strftime('%d-%m-%Y %H:%M:%S')}")
    return start_time


def execution_time(start_time):
    exec_time = (dt.datetime.now() - start_time).seconds
    disp_md(f"INFO: Notebook execution finished --- Elapsed time {exec_time} seconds ---")
    return exec_time




def disp_md(md_input, font_size=16, color='white'):
    # Check if the input is a Path object or a string path to a file that exists
    if isinstance(md_input, Path) or (isinstance(md_input, str) and Path(md_input).is_file()):
        md_path = Path(md_input)
        try:
            # Specify the encoding; 'utf-8' is a common encoding that might solve the issue
            md_content = md_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            return
    else:
        # Assume the input is a markdown string
        md_content = f"\n{md_input}"

    # Apply the styling to the markdown content using HTML and CSS
    styled_md = f"\n<div style='font-size: {font_size}px; color: {color};'>{md_content}</div>"

    # Display the styled markdown content
    display(Markdown(styled_md))


# # Usage examples:
# disp_md('# This is a markdown string')
# disp_md(Path('1_logfiles-to-parquet.md'))
# disp_md('1_logfiles-to-parquet.md')  # If it's a valid file path

def disp_md_block(md_str, font_size=16):
    display(Markdown(md_str))
