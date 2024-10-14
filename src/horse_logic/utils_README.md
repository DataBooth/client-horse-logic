# Python Utility Functions

This module provides a collection of utility functions for various tasks in Python, including displaying class definitions, configuring logging, exporting data to CSV, and creating database tables from SQL files (.sql).

## Features

- Display class definitions in Markdown format
- Set custom logger format
- Export pandas DataFrames to CSV files with logging
- Create database tables from SQL files

## Dependencies

- pandas
- IPython
- loguru

## Usage

Import the required functions from this module and use them in your Python scripts or Jupyter notebooks.

Example:

```python
from utility_functions import display_class_definition, export_data_to_csv

# Display a class definition
display_class_definition(MyClass)

# Export a DataFrame to CSV
df = pd.DataFrame(...)
export_data_to_csv(df, info_message="Sample data", filepath="sample.csv")
