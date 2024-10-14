import inspect
import sys
from pathlib import Path

import duckdb
import pandas as pd
from IPython.display import Markdown, display
from loguru import logger


def display_class_definition(class_name: type) -> None:
    """
    Display the source code of a given class using Markdown formatting.

    Args:
        class_name (type): The class whose source code is to be displayed.

    Returns:
        None
    """
    display(Markdown(f"```{inspect.getsource(class_name)}```"))


def set_custom_logger_format() -> None:
    """
    Set a custom format for the logger without the function call information for ease of readability.

    This function removes the default handler and adds a new one with a custom format.

    Returns:
        None
    """
    custom_format_no_func_info = "<level>{level: <8}</level> | <level>{message}</level>"
    logger.remove()  # Remove the default handler before adding a new one
    logger.add(sys.stderr, format=custom_format_no_func_info)


def export_data_to_csv(
    df: pd.DataFrame, info_message: str = None, filepath: str = None, header: list = None
) -> None:
    """
    Export a DataFrame to a CSV file and log the operation.

    Args:
        df (pd.DataFrame): The DataFrame to be exported.
        info_message (str, optional): Additional information to be included in the log message.
        filepath (str, optional): The path where the CSV file will be saved.
        header (list, optional): Column names to be used as the header in the CSV file.

    Returns:
        None
    """
    df.to_csv(filepath, header=header)
    logger.info(f"{len(df)} rows - {info_message}: {filepath}")
    create_markdown_link(filepath)


def create_tables_from_sql_file(
    con: duckdb.DuckDBPyConnection, file_path: str, echo_sql: bool = False
) -> None:
    """
    Create tables in a DuckDB database from SQL commands in a file.

    Args:
        con (duckdb.DuckDBConnection): The DuckDB database connection object.
        file_path (str): The path to the SQL file containing table creation commands.
        echo_sql (bool, optional): If True, display the SQL commands using Markdown formatting.

    Returns:
        None
    """
    with open(file_path, "r") as file:
        sql_commands = file.read()
    if echo_sql:
        display(Markdown(f"\n```\n{sql_commands}\n```"))
    con.execute(sql_commands)


def create_markdown_link(file_path, link_text=None):
    """
    Creates a Markdown link for a given file path that works in both
    Jupyter notebooks and when rendered to HTML by Quarto.

    Parameters:
    - file_path (str or Path): The path to the file, relative to the notebooks directory.
    - link_text (str, optional): The text to display for the link.

    Returns:
    - tuple: (markdown_link, debug_info)
    """
    # Convert to Path object if it's a string
    file_path = Path(file_path)

    relative_path = Path(file_path).relative_to(Path.cwd())
    
    # Resolve the full path of the target file
    full_path = (Path.cwd() / file_path).resolve()
    
    # Check if the file exists
    if not full_path.exists():
        raise FileNotFoundError(f"The file {full_path} does not exist.")
    
    # Use the file name as link_text if not provided
    if link_text is None:
        # link_text = file_path.name
        link_text = str(relative_path)

    # Create Markdown link
    markdown_link = f"[{link_text}]({relative_path})"

    # Debug information
    debug_info = {
        "current_dir": str(Path.cwd()),
        "full_path": str(full_path),
        "relative_path": str(file_path),
        "file_path_input": str(file_path)
    }

    display(Markdown(markdown_link))
    return markdown_link, debug_info