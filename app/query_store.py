from datetime import datetime

import duckdb


# TODO: The backend query store vs the data for analytic queries is being confused here by GPT4 I think
class QuerySuggestion:
    # ... (methods for suggesting queries based on data)
    pass


class QueryStore:
    def __init__(self):
        self.conn = duckdb.connect(database="query_store.duckdb", read_only=False)
        self.create_if_not_exists()

    def save_query(self, name, description, author, query_sql):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            """
            INSERT INTO query_store (name, description, author, query_sql, last_modified_date, run_count)
            VALUES (?, ?, ?, ?, ?, 0)
        """,
            (name, description, author, query_sql, current_time),
        )

    def get_saved_queries_ordered_by_run_count(self):
        result = self.conn.execute(
            """
            SELECT name, description, author, query_sql, last_modified_date, run_count
            FROM query_store
            ORDER BY run_count DESC
        """
        ).fetchall()
        return result

    def increment_query_run_count(self, name):
        self.conn.execute(
            """
            UPDATE query_store
            SET run_count = run_count + 1
            WHERE name = ?
        """,
            (name,),
        )

    def create_if_not_exists(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS query_store (
                name TEXT PRIMARY KEY,
                description TEXT,
                author TEXT,
                query_sql TEXT,
                last_modified_date TIMESTAMP,
                run_count INTEGER DEFAULT 0
            )
        """
        )
