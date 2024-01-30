import duckdb

# import pandas as pd
# from pathlib import Path


class DatabaseConnection:
    def __init__(self, datasource_info):
        self.datasource_info = datasource_info
        self.report = {"connection": None, "tables_created": []}
        self.connection = self.create_connection()
        self.tables = self.get_user_tables()

    def create_connection(self):
        # Get the database file path from datasource_info or default to in-memory if not provided
        db_path = self.datasource_info.get("path", ":memory:")

        # print(f'Connection string: {db_path}')

        # Connect directly to the specified DuckDB database file
        con = duckdb.connect(database=db_path.as_posix() if db_path != ":memory:" else db_path)

        # Connect to DuckDB, either in-memory or using a specific file

        if self.datasource_info["type"] == "database":
            db_path = self.datasource_info["path"]
            if db_path.suffix in [".duckdb", ".ddb", ".sqlite"]:
                # If the database is a file, attach it to DuckDB
                con = duckdb.connect(database=db_path.as_posix())
            else:
                raise ValueError(f"Unsupported database file type: {db_path.suffix}")
        elif self.datasource_info["type"] in ["parquet", "csv"]:
            # Create tables from files in an in-memory DuckDB connection
            con = duckdb.connect()
            self.create_tables_from_files(con)
        else:
            raise ValueError("Unsupported datasource type.")

        return con

    def create_tables_from_files(self, con):
        for file_path in self.datasource_info["paths"]:
            table_name = self.get_valid_table_name(file_path.stem)
            file_extension = file_path.suffix.lower()

            if file_extension == ".parquet":
                con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_parquet('{file_path}');")
            elif file_extension == ".csv":
                con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_path}');")
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            self.report["tables_created"].append(
                f"Table `{table_name}` created from file '{file_path.name}'"
            )

    def show_details(self):
        # Echo the connection details
        print(self.report["connection"])
        # Echo the details of the tables created
        for table_report in self.report["tables_created"]:
            print(table_report)

    def get_user_tables(self):
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main';"
        cursor = self.connection.execute(query)
        tables = cursor.fetchall()
        # Extract table names from the tuples returned by fetchall
        table_names = [table[0] for table in tables]
        return table_names

    @staticmethod
    def get_valid_table_name(stem):
        # Implement any necessary logic to ensure the stem is a valid DuckDB table name
        return stem.replace("-", "_").lower()

    def execute(self, query, params=None):
        cursor = self.connection.cursor()
        # print(f"Schema query: {query}")
        cursor.execute(query, params or ())
        # If the query is a SELECT statement, fetch the results
        if query.strip().upper().startswith("SELECT"):
            return cursor.fetchall()
        else:
            self.connection.commit()
            return None  # For non-query operations, return None

    def query_df(self, sql_query):
        # print(sql_query)
        return self.connection.execute(sql_query).fetchdf()

    def close_connection(self):
        self.connection.close()
