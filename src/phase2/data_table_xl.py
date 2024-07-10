import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from pathlib import Path

INFO_SHEET_NAME = "Info"


class DataManagerXL:
    def __init__(self, workbook):
        self.workbook = Path(workbook)

    def get_worksheet_names(self):
        """
        Returns a list of the names of all worksheets in the workbook.
        """
        try:
            wb = openpyxl.load_workbook(self.workbook)
            return wb.sheetnames
        except FileNotFoundError:
            raise Exception(f"The workbook {self.workbook} does not exist or is not accessible.")

    def read_table_data(
        self,
        sheet_name,
        skip_info_sheet=True,
        use_first_col_as_index=False,
        rows=None,
        columns=None,
        range=None,
        types=None,
    ):
        # Check if the workbook exists and is accessible
        try:
            wb = openpyxl.load_workbook(self.workbook)
        except FileNotFoundError:
            raise Exception(f"The workbook {self.workbook} does not exist or is not accessible.")

        # Skip reading the Info sheet if skip_info_sheet is True
        if skip_info_sheet and sheet_name == INFO_SHEET_NAME:
            print(
                f"INFO: Skipping the '{INFO_SHEET_NAME}' worksheet. If unintended set skip_info_sheet=False in read_table_data method."
            )
            return None  # Or appropriate response indicating no data was read

        # Ensure a sheet name is provided
        if sheet_name is None:
            raise Exception("A sheet name must be defined to read Excel data.")

        # Check if the sheet name exists in the workbook
        if sheet_name not in wb.sheetnames:
            raise Exception(
                f"The sheet name {sheet_name} does not exist in the workbook {self.workbook}."
            )

        # Preliminary read of the data to facilitate debugging
        try:
            df_debug = pd.read_excel(self.workbook, sheet_name=sheet_name, header=0)
        except Exception as e:
            raise Exception(f"Failed to read sheet {sheet_name} for debugging purposes: {str(e)}")

        # Example check: Sheet is empty
        if df_debug.empty:
            raise Exception(
                f"The sheet {sheet_name} in the workbook {self.workbook} is empty. Data preview: \n{df_debug.head(2)}"
            )

        # Adjust the read_excel call based on use_first_col_as_index and other parameters
        usecols = (
            range(0, columns + 1)
            if use_first_col_as_index
            else range(1, columns + 1)
            if columns is not None
            else None
        )
        try:
            df = pd.read_excel(
                self.workbook,
                sheet_name=sheet_name,
                header=0,
                index_col=0 if use_first_col_as_index else None,
                nrows=rows,
                usecols=usecols,
            )
        except Exception as e:
            raise Exception(
                f"Failed to read sheet {sheet_name} with specified parameters: {str(e)}\nData preview: \n{df_debug.head(2)}"
            )

        # Check if the list of column types is valid and matches the data types of the columns
        if types is not None:
            if not isinstance(types, list) or len(types) != len(df.columns):
                raise Exception(
                    f"The list of column types {types} is not valid. It must be a list of length {len(df.columns)}. Data preview: \n{df.head(2)}"
                )
            else:
                # Convert the data types of the columns according to the list
                for i, t in enumerate(types):
                    try:
                        df.iloc[:, i] = df.iloc[:, i].astype(t)
                    except ValueError:
                        raise Exception(
                            f"The column type {t} does not match the data type of the column {df.columns[i]}. Data preview: \n{df.head(2)}"
                        )

        return df

    # A method that exports every table from each worksheet in a workbook into CSV format
    def export_excel_data(self):
        # Check if the workbook exists and is accessible
        try:
            wb = openpyxl.load_workbook(self.workbook)
        except FileNotFoundError:
            raise Exception(f"The workbook {self.workbook} does not exist or is not accessible.")

        # Loop through each sheet in the workbook
        for sheet in wb.sheetnames:
            # Check if the sheet is not empty
            ws = wb[sheet]
            if not (ws.max_row == 1 and ws.max_column == 1 and ws["A1"].value is None):
                # Check if there is only one table in the sheet
                if (
                    ws["A1"].value is None
                    and all(ws.cell(row=1, column=c).value is None for c in range(2, ws.max_column + 1))
                    and all(ws.cell(row=r, column=1).value is None for r in range(2, ws.max_row + 1))
                ):
                    raise Exception(
                        f"The sheet {sheet} in the workbook {self.workbook} has more than one table. Only one table per sheet is allowed."
                    )
                else:
                    # Read the data from the sheet into a dataframe
                    df = pd.read_excel(self.workbook, sheet_name=sheet, header=0, index_col=0)
                    # Generate the file name for the CSV file
                    file_name = f"{self.workbook.stem}_{sheet}.csv"
                    # Write the dataframe to the CSV file
                    df.to_csv(file_name, sep=",", index=False)
                    # Print a message to indicate the export is done
                    print(f"Exported the table from sheet {sheet} to CSV file {file_name}.")

        # Print a message to indicate the export is done for all sheets
        print(f"Exported all tables from workbook {self.workbook} to CSV files.")

    # A method that creates a workbook based on a set of tables in appropriately named CSV files
    def create_excel_data(self, files):
        # Check if the files are a list of CSV files
        if not isinstance(files, list) or not all(Path(f).suffix == ".csv" for f in files):
            raise Exception(f"The files {files} are not a list of CSV files.")

        # Create a new workbook
        wb = openpyxl.Workbook()
        # Remove the default sheet
        wb.remove(wb.active)

        for file in files:
            # Use pathlib to handle file paths
            file_path = Path(file)
            # Read the data from the CSV file into a dataframe
            df = pd.read_csv(file_path, sep=",")

            # Extract the sheet name from the file name (assuming the format 'workbookname_sheetname.csv')
            # If your file naming convention is different, adjust the split logic accordingly
            sheet_name = file_path.stem.split("_")[-1]

            # Check if the sheet name is valid
            if not sheet_name.isalnum():
                raise Exception(
                    f"The sheet name {sheet_name} derived from {file} is not valid. It must be alphanumeric."
                )

            # Create a new sheet in the workbook with the extracted sheet name
            ws = wb.create_sheet(sheet_name)

            # Write the dataframe to the sheet
            for r in dataframe_to_rows(
                df, index=False, header=True
            ):  # Set index=False if you don't want to include DataFrame index
                ws.append(r)

        # Generate the workbook name (assuming all CSV files belong to the same workbook, using the first file's name)
        workbook_name = (
            file_path.parts[-1].split("_")[0] + ".xlsx"
        )  # Adjust this line if your naming convention is different

        # Save the workbook
        workbook_path = (
            file_path.parent / workbook_name
        )  # Save the workbook in the same directory as the CSV files
        wb.save(workbook_path)
        print(f"Created a workbook {workbook_path} based on the tables in CSV files {files}.")


# Lookup helper functions


def lookup_by_index(df, index, column_name):
    try:
        value = df.loc[index, column_name]
        return value
    except KeyError:
        return "Index or column name not found."


def lookup_by_row_value(df, search_column, search_value, target_column):
    filtered_df = df[df[search_column] == search_value]
    if not filtered_df.empty:
        try:
            value = filtered_df[target_column].iloc[0]
            return value
        except KeyError:
            return "Target column name not found."
    else:
        return "No matching row found."


if __name__ == "__main__":
    data_manager = DataManagerXL(workbook="path/to/workbook.xlsx")

    # Reading data from a specific sheet with custom configurations
    table_data = data_manager.read_table_data(
        sheet_name="Sheet1", use_first_col_as_index=True, rows=100, columns=5
    )
