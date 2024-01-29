import sqlglot
import duckdb
from pathlib import Path

def validate_sql(sql_text, dialect='duckdb'):
    try:
        # Parse and validate the SQL using the specified dialect
        expressions = sqlglot.parse(sql_text, read=dialect)
        # Generate the SQL again to ensure it's valid
        sqlglot.to_sql(expressions)
        print("SQL validation successful.")
        return True
    except sqlglot.errors.ParseError as e:
        print(f"SQL validation failed: {e}")
        return False

def execute_sql_file(file_path, db_path=':memory:'):
    # Read the SQL file
    with open(file_path, 'r') as file:
        sql_text = file.read()

    # Validate the SQL
    # if validate_sql(sql_text):
    # Connect to DuckDB
    con = duckdb.connect(db_path)
    try:
        # Execute the SQL query
        con.execute(sql_text)
        print("SQL executed successfully.")
    except Exception as e:
        print(f"Failed to execute SQL: {e}")
    finally:
        con.close()

# Replace 'path/to/your/sqlfile.sql' with the path to your SQL file

sql_file = "/Users/mjboothaus/code/github/databooth/horse-logic/sql/create_tables_duckdb.sql"

if Path(sql_file).exists():
    execute_sql_file(sql_file, db_path="experiments_Oct2023.ddb")
else:
    raise FileNotFoundError(f"ERROR: File not found - {sql_file}")
