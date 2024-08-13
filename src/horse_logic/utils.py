import inspect
import sys

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
