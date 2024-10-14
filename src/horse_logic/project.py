import itables.options as opt
from itables import init_notebook_mode
import duckdb
import pandas as pd
from pathlib import Path
from contextlib import contextmanager
from IPython.display import display, Markdown
import sys
from loguru import logger


class Project:
    def __init__(self, db_name=None, project_root=None, table_page_length=10):
        self._db_name = db_name
        self._db_connection = None
        self._root = project_root
        self._initialize_logger()
        if self._db_name is None:
            logger.info("Project does not have a database.")
        self._initialize_itables(table_page_length)
        logger.info(f"Project: table page length set to: {table_page_length}")


    def _initialize_logger(self, format="<level>{level: <8}</level> | <level>{message}</level>"):
        logger.remove()  # Remove default handler
        logger.add(sys.stderr, format=format)

    def _initialize_itables(self, table_page_length=10):
        init_notebook_mode(all_interactive=True, connected=False)
        opt.pageLength = table_page_length

    def get_db_connection(self):
        if self._db_name is None:
            return None
        if self._db_connection is None:
            if self._db_name == "":
                # Use in-memory database
                self._db_connection = duckdb.connect(":memory:")
                logger.info("Connected to in-memory database")
            else:
                # Use file-based database
                self._db_connection = duckdb.connect(self._db_name)
                logger.info(f"Connected to database: {self._db_name}")
        return self._db_connection

    @contextmanager
    def db_connection(self):
        conn = self.get_db_connection()
        if conn is None:
            logger.warning("No database connection available")
            yield None
        else:
            try:
                yield conn
            finally:
                conn.commit()  # Commit changes but don't close the connection

    def create_tables_from_sql_file(self, file_path: str, echo_sql: bool = False):
        conn = self.get_db_connection()
        if conn is None:
            logger.warning("No database connection available. Skipping table creation.")
            return

        with self.db_connection() as conn:
            file_path = Path(file_path)
            with open(file_path, "r") as file:
                sql_commands = file.read()
            if echo_sql:
                display(Markdown(f"\n```sql\n{sql_commands}\n```"))
            conn.execute(sql_commands)
            logger.info(f"Tables created successfully from {file_path}")

    def close_db_connection(self):
        if self._db_connection:
            self._db_connection.close()
            self._db_connection = None
            logger.info("Database connection closed")

    def __del__(self):
        self.close_db_connection()

    def export_data_to_csv(
        self,
        df: pd.DataFrame,
        filepath: str,
        info_message: str = None,
        header: list = None,
        log_relative_path: bool = True,
    ):
        filepath = Path(filepath)
        df.to_csv(filepath, header=header)

        if log_relative_path:
            try:
                # Get the relative path from the current working directory
                cwd = Path.cwd()
                relative_path = filepath.relative_to(cwd)
                path_info = f"Relative path: {relative_path}"
            except ValueError:
                # If the file is not under the current working directory,
                # fall back to absolute path
                path_info = f"Absolute path: {filepath}"
        else:
            path_info = f"Path: {filepath}"

        log_message = f"{len(df)} rows exported to CSV."  # {path_info}"
        if info_message:
            log_message = f"{info_message}. {log_message}"

        logger.info(log_message)

        if filepath.exists():
            self.create_markdown_link(relative_path)
        else:
            logger.warning(f"File not found: {filepath}. Markdown link not created.")

    def create_markdown_link(self, file_path, link_text=None):
        file_path = Path(file_path)
        project_root = self.get_root_dir()
        cwd = Path.cwd()

        # Get the path relative to the project root for the actual link
        try:
            link_path = file_path.relative_to(project_root)
        except ValueError:
            link_path = file_path

        # Get the path relative to the current working directory for display
        try:
            display_path = file_path.relative_to(cwd)
        except ValueError:
            display_path = file_path

        full_path = file_path.resolve()

        if not full_path.exists():
            raise FileNotFoundError(f"The file {full_path} does not exist.")

        if link_text is None:
            link_text = str(display_path)

        markdown_link = f"[{link_text}]({link_path})"

        debug_info = {
            "current_dir": str(cwd),
            "project_root": str(project_root),
            "full_path": str(full_path),
            "link_path": str(link_path),
            "display_path": str(display_path),
            "file_path_input": str(file_path),
        }

        display(Markdown(markdown_link))
        # logger.debug(f"Markdown link debug info: {debug_info}")
        return markdown_link, debug_info

    def get_root_dir(self):
        if self._root is None:
            self._root = self.find_project_root()
            logger.info(f"Project directory: {self._root}")
        return self._root

    def find_project_root(self, marker="pyproject.toml"):
        path = Path.cwd().resolve()
        while path != path.parent:
            if (path / marker).exists():
                return path
            path = path.parent
        raise FileNotFoundError(f"Could not find project root with marker: {marker}")


# Usage example
# if __name__ == "__main__":
#     project = Project(db_name='my_project.db', table_page_length=20)  # Override default page length
#     # or
#     project = Project(db_name='my_project.db')  # Use default page length of 10

#     # Create tables
#     project.create_tables_from_sql_file('sql/create_tables.sql', echo_sql=True)

#     # Export data
#     df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
#     project.export_data_to_csv(df, 'data/output.csv', "Sample data export")

#     # Create markdown link
#     project.create_markdown_link('data/output.csv', "Link to CSV")

#     # Use database connection
#     with project.db_connection() as conn:
#         result = conn.execute("SELECT * FROM my_table").fetchall()
#         print(result)

#     # Project root
#     print(f"Project root: {project.get_root_dir()}")
