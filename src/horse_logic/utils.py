import inspect
import sys

import pandas as pd
from IPython.display import display, Markdown
from loguru import logger


def display_class_definition(class_name):
    display(Markdown(f"```{inspect.getsource(class_name)}```"))


def set_custom_logger_format():
    custom_format_no_func_info = "<level>{level: <8}</level> | <level>{message}</level>"
    logger.remove()  # Remove the default handler before adding a new one
    logger.add(sys.stderr, format=custom_format_no_func_info)


def export_data_to_csv(df, info_message=None, filepath=None, header=None):
    df.to_csv(filepath, header=header)
    logger.info(f"{len(df)} rows - {info_message}: {filepath}")

def create_tables_from_sql_file(con, file_path, echo_sql=False):
    with open(file_path, "r") as file:
        sql_commands = file.read()
    if echo_sql:
        display(Markdown(f"\n```\n{sql_commands}\n```"))
    con.execute(sql_commands)
