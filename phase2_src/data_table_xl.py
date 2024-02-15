import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from pathlib import Path


# A class that represents an Excel data manager
class DataTableXL:
    # A constructor that initializes the attributes
    def __init__(self, workbook, sheet, rows=None, columns=None, range=None, types=None):
        self.workbook = workbook
        self.sheet = sheet
        self.rows = rows
        self.columns = columns
        self.range = range
        self.types = types

    # A method that reads data from the specified excel workbook and sheet name into a dataframe
    def read_excel_data(self):
        # Check if the workbook exists and is accessible
        try:
            wb = openpyxl.load_workbook(self.workbook)
        except FileNotFoundError:
            raise Exception(f"The workbook {self.workbook} does not exist or is not accessible.")

        # Check if the sheet name exists and is not empty
        if self.sheet not in wb.sheetnames:
            raise Exception(
                f"The sheet name {self.sheet} does not exist in the workbook {self.workbook}."
            )
        ws = wb[self.sheet]
        if ws.max_row == 1 and ws.max_column == 1 and ws["A1"].value is None:
            raise Exception(f"The sheet {self.sheet} in the workbook {self.workbook} is empty.")

        # Check if the table starts from cell A1 and has column headings in row 1 and row numbers in column 1
        if (
            ws["A1"].value is not None
            or any(ws.cell(row=1, column=c).value is None for c in range(2, ws.max_column + 1))
            or any(ws.cell(row=r, column=1).value is None for r in range(2, ws.max_row + 1))
        ):
            raise Exception(
                f"The table in the sheet {self.sheet} does not start from cell A1 or does not have column headings in row 1 or row numbers in column 1."
            )

        # Check if the named range exists and is valid
        if self.range is not None:
            if self.range not in wb.defined_names:
                raise Exception(
                    f"The named range {self.range} does not exist in the workbook {self.workbook}."
                )
            else:
                # Get the coordinates of the named range
                dests = wb.defined_names[self.range].destinations
                # Check if the named range is in the same sheet and is a single range
                if len(dests) != 1 or dests[0][0] != self.sheet:
                    raise Exception(
                        f"The named range {self.range} is not in the same sheet or is not a single range."
                    )
                else:
                    # Get the top left and bottom right cells of the named range
                    min_row, min_col, max_row, max_col = openpyxl.utils.range_boundaries(dests[0][1])
                    # Check if the named range includes the column headings and row numbers
                    if min_row != 1 or min_col != 1:
                        raise Exception(
                            f"The named range {self.range} does not include the column headings and row numbers."
                        )
                    # Override the rows and columns attributes with the size of the named range
                    self.rows = max_row - min_row + 1
                    self.columns = max_col - min_col + 1

        # Check if the number of rows and columns are valid
        if self.rows is None:
            self.rows = ws.max_row - 1  # Exclude the header row
        elif not isinstance(self.rows, int) or self.rows < 1 or self.rows > ws.max_row - 1:
            raise Exception(
                f"The number of rows {self.rows} is not valid. It must be an integer between 1 and {ws.max_row - 1}."
            )

        if self.columns is None:
            self.columns = ws.max_column - 1  # Exclude the index column
        elif not isinstance(self.columns, int) or self.columns < 1 or self.columns > ws.max_column - 1:
            raise Exception(
                f"The number of columns {self.columns} is not valid. It must be an integer between 1 and {ws.max_column - 1}."
            )

        # Read the data from the excel sheet into a dataframe
        df = pd.read_excel(
            self.workbook,
            sheet_name=self.sheet,
            header=0,
            index_col=0,
            nrows=self.rows,
            usecols=range(1, self.columns + 1),
        )

        # Check if the list of column types is valid and matches the data types of the columns
        if self.types is not None:
            if not isinstance(self.types, list) or len(self.types) != self.columns:
                raise Exception(
                    f"The list of column types {self.types} is not valid. It must be a list of length {self.columns}."
                )
            else:
                # Convert the data types of the columns according to the list
                for i, t in enumerate(self.types):
                    try:
                        df.iloc[:, i] = df.iloc[:, i].astype(t)
                    except ValueError:
                        raise Exception(
                            f"The column type {t} does not match the data type of the column {df.columns[i]}."
                        )

        # Return the dataframe
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
                    file_name = self.workbook.split(".")[0] + "_" + sheet + ".csv"
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
