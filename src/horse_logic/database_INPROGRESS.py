import duckdb
from pathlib import Path
from loguru import logger
from dataclasses import asdict


class Database:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self._connection = None

    def connect(self):
        if self._connection is None:
            self._connection = duckdb.connect(str(self.db_path))
        return self._connection

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    def execute(self, query, params=None):
        conn = self.connect()
        return conn.execute(query, params)

    def get_last_insert_id(self, table_name):
        query = f"SELECT MAX(ROWID) FROM {table_name}"
        result = self.execute(query).fetchone()[0]
        return result if result is not None else 0

    def insert_record(self, table_name, record):
        columns = ", ".join(record.keys())
        placeholders = ", ".join("?" for _ in record)
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.execute(query, tuple(record.values()))
        self.connect().commit()

    def insert_record_to_cb_database(self, record, table_name):
        self.insert_record(table_name, record)

    def get_version(self):
        try:
            version_query = "SELECT version();"
            result = self.execute(version_query).fetchone()
            return str(result[0]) if result else "Unable to retrieve DuckDB version"
        except Exception as e:
            return f"Error retrieving DuckDB version: {str(e)}"

    def create_tables_from_sql_file(self, sql_path):
        with open(sql_path, "r") as file:
            sql_commands = file.read()
        self.execute(sql_commands)
        logger.info(f"Tables created successfully from {sql_path}")

    def run_multiple_queries(self, sql: str):
        queries = [q.strip() for q in sql.split(";") if q.strip()]
        results = []
        for query in queries:
            result = self.execute(query).fetchall()
            results.append(result)
        return results
