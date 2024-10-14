import duckdb
import pandas as pd
from pathlib import Path
from contextlib import contextmanager
from IPython.display import display, Markdown
import sys
from loguru import logger
import itables.options as opt
from itables import init_notebook_mode

class Project:
    def __init__(self, project_root=None, experiment_type=None, table_page_length=10):
        self._root = project_root or self.find_project_root()
        self.experiment_type = experiment_type
        logger.info(f"Experiment type: {self.experiment_type}")
        self._db_connection = None
        self._db_name = None
        self._initialize_logger()
        self._initialize_itables(table_page_length)
        logger.info(f"Table page length set to: {table_page_length}")

    def _initialize_logger(self, format="<level>{level: <8}</level> | <level>{message}</level>"):
        logger.remove()  # Remove default handler
        logger.add(sys.stderr, format=format)

    def _initialize_itables(self, table_page_length=10):
        init_notebook_mode(all_interactive=True, connected=False)
        opt.pageLength = table_page_length

    def setup_database(self, db_name=None):
        if db_name is None and self.experiment_type:
            data_dir = self._root / "data"
            db_name = data_dir / f"Experiments_{self.experiment_type}_2023_Q4.ddb"
        
        if db_name:
            self._db_name = str(db_name)
        else:
            self._db_name = ""  # In-memory database
        
        # Close existing connection if any
        self.close_db_connection()
        
        # Create new connection
        self._db_connection = duckdb.connect(self._db_name)
        logger.info(f"Connected to database: {self._db_name}")

    def get_db_connection(self):
        if self._db_connection is None:
            self.setup_database()
        return self._db_connection

    @contextmanager
    def db_connection(self):
        conn = self.get_db_connection()
        try:
            yield conn
        finally:
            conn.commit()  # Commit changes but don't close the connection

    def create_tables_from_sql_file(self, sql_file):
        conn = self.get_db_connection()
        sql_path = self.sql_dir / sql_file
        with open(sql_path, "r") as file:
            sql_commands = file.read()
        conn.execute(sql_commands)
        logger.info(f"Tables created successfully from {sql_path}")

    def close_db_connection(self):
        if self._db_connection:
            self._db_connection.close()
            self._db_connection = None
            logger.info("Database connection closed")

    def __del__(self):
        self.close_db_connection()

    def get_root_dir(self):
        return self._root

    def find_project_root(self, marker="pyproject.toml"):
        path = Path.cwd().resolve()
        while path != path.parent:
            if (path / marker).exists():
                return path
            path = path.parent
        raise FileNotFoundError(f"Could not find project root with marker: {marker}")

    @property
    def data_dir(self):
        return self._root / "data"

    @property
    def sql_dir(self):
        return self._root / "sql"

    def export_data_to_csv(self, df: pd.DataFrame, filepath: str, info_message: str = None, header: list = None, log_relative_path: bool = True):
        filepath = Path(filepath)
        df.to_csv(filepath, header=header)
        
        if log_relative_path:
            try:
                relative_path = filepath.relative_to(Path.cwd())
                path_info = f"Relative path: {relative_path}"
            except ValueError:
                path_info = f"Absolute path: {filepath}"
        else:
            path_info = f"Path: {filepath}"
        
        log_message = f"{len(df)} rows exported to CSV." # {path_info}"
        if info_message:
            log_message = f"{info_message}. {log_message}"
        
        logger.info(log_message)
        
        if filepath.exists():
            self.create_markdown_link(filepath)
        else:
            logger.warning(f"File not found: {filepath}. Markdown link not created.")

    def create_markdown_link(self, file_path, link_text=None, working_dir="notebooks"):
        file_path = Path(file_path).resolve()
        project_root = self.get_root_dir()
        working_dir_path = project_root / working_dir

        # Ensure the file exists
        if not file_path.exists():
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        # Calculate the link path relative to the working directory
        try:
            link_path = file_path.relative_to(working_dir_path)
        except ValueError:
            # If the file is not under the working directory, 
            # calculate the path relative to the project root
            try:
                link_path = file_path.relative_to(project_root)
            except ValueError:
                # If it's not under the project root, use the absolute path
                link_path = file_path

        # Calculate the display path relative to the current working directory
        try:
            display_path = file_path.relative_to(Path.cwd())
        except ValueError:
            display_path = file_path

        if link_text is None:
            link_text = str(display_path)

        markdown_link = f"[{link_text}]({link_path})"

        debug_info = {
            "current_dir": str(Path.cwd()),
            "project_root": str(project_root),
            "working_dir": str(working_dir_path),
            "full_path": str(file_path),
            "link_path": str(link_path),
            "display_path": str(display_path),
            "file_path_input": str(file_path)
        }

        display(Markdown(markdown_link))
        #logger.debug(f"Markdown link debug info: {debug_info}")
        return markdown_link, debug_info

    def display_sessions_by_subject(self, df_summary, subject_df):
        session_summary = []
        for n_subject, subject_name in enumerate(subject_df["subject_name"]):
            df_ = df_summary.drop(columns=["suffix", "subject_name"])[
                df_summary["subject_name"] == subject_name
            ]
            n_session = len(df_)
            session_summary.append((n_subject + 1, subject_name.capitalize(), n_session))
            if n_session == 0:
                logger.info(f"Subject {subject_name}: No experiments conducted")
            else:
                df_.loc[:, "time_dff"] = df_["datetime"].diff()
                display(Markdown(f"### {n_subject+1}. {subject_name.capitalize()}: {n_session} session(s)"))
                display(df_)
        return pd.DataFrame(session_summary, columns=["Subject number", "Subject name", "Session count"])


    def get_subject_info(self):
        HORSE_ORDER_XLSX = "Cohort data for MB.xlsx"
        HORSE_ORDER_PATH = self._root / "docs" / "from_CH"
        HORSE_ORDER_FILEPATH = HORSE_ORDER_PATH / HORSE_ORDER_XLSX

        if HORSE_ORDER_FILEPATH.exists():
            subject_df = pd.read_excel(HORSE_ORDER_FILEPATH)
            logger.info(f"Loaded horse order info from: {HORSE_ORDER_FILEPATH}")

            subject_df.rename(
                {"No": "subject_number", "Horse": "subject_name"}, axis=1, inplace=True
            )  # Rename columns
            
            # Ensure lower case subject names for later lookup
            subject_df["subject_name"] = subject_df["subject_name"].str.lower()
            
            # Create and log the sorted subject list
            sorted_subjects = sorted(subject_df["subject_name"].to_list())
            subject_list = self._format_subject_list(sorted_subjects)
            
            logger.info(f"Subject count: {len(sorted_subjects)}")
            logger.info(f"Sorted subject names:\n{subject_list}")

            return subject_df
        else:
            logger.error(f"Horse order info not found: {HORSE_ORDER_FILEPATH}")
            return None

    def _format_subject_list(self, subjects, width=100, indent="\t"):
        formatted_list = indent
        line_length = len(indent)
        for subject in subjects:
            if line_length + len(subject) + 2 > width:  # +2 for ", "
                formatted_list += "\n" + indent
                line_length = len(indent)
            formatted_list += subject + ", "
            line_length += len(subject) + 2
        return formatted_list.rstrip(", ")  # Remove trailing comma and space


# Usage example
# if __name__ == "__main__":
#     # Initialise the project
#     project = Project(experiment_type="RPE", table_page_length=20)

#     # Get directories
#     PROJECT_DIR = project.get_root_dir()
#     DATA_DIR = project.data_dir
#     SQL_DIR = project.sql_dir

#     # Setup the database
#     project.setup_database()  # This will use the default database name based on the experiment type

#     # Create tables
#     project.create_tables_from_sql_file("create_experiment_tables_ddb.sql")

  # Get subject info
    # subject_df = project.get_subject_info()

#     # Export some data
#     df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
#     project.export_data_to_csv(df, DATA_DIR / "sample_data.csv", "Sample data export")

#     # Create a markdown link
#     project.create_markdown_link(DATA_DIR / "sample_data.csv", "Link to sample data")

#     # Close the database connection when done
#     project.close_db_connection()