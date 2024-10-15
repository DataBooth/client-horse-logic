import sys
import urllib.parse
from contextlib import contextmanager
from pathlib import Path

import duckdb
import itables.options as opt
import pandas as pd
import yaml
from IPython.display import HTML, Markdown, display
from itables import init_notebook_mode
from loguru import logger
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename


class Project:
    def __init__(self, config_file='project_config.yaml', experiment_type=None, table_page_length=10, delete_existing_db=True):
        self.project_dir = self._find_project_root()
        self.config = self.load_config(config_file)
        self.experiment_type = experiment_type
        self._db_connection = None
        self._initialise_logger()
        self._initialise_itables(table_page_length)
        self._initialise_directories()
        self._initialise_database(delete_existing_db)
        logger.info(f"Project initialised ({experiment_type}): config defined in {config_file}")

    def _find_project_root(self):
        current_dir = Path.cwd()
        while current_dir.name != 'notebooks':
            if (current_dir / 'project_config.yaml').exists():
                return current_dir
            current_dir = current_dir.parent
        return current_dir.parent  # Return the parent of 'notebooks'

    def load_config(self, config_file):
        config_path = self.project_dir / config_file
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _initialise_logger(self):
        logger.remove()  # Remove default handler
        logger.add(sys.stderr, format="<level>{level: <8}</level> | <level>{message}</level>")

    def _initialise_itables(self, table_page_length=10):
        init_notebook_mode(all_interactive=True, connected=False)
        opt.pageLength = table_page_length

    def _initialise_directories(self):
        for name, info in self.config['directories'].items():
            self.initialise_dir(name, info)

    def initialise_dir(self, name, info):
        if isinstance(info['path'], dict):
            # If path is a dict, assume it contains experiment-specific paths
            if self.experiment_type not in info['path']:
                raise ValueError(f"No path defined for experiment type '{self.experiment_type}' in directory '{name}'")
            path = info['path'][self.experiment_type]
        else:
            # If path is a string, use it directly
            path = info['path']

        full_path = self.project_dir / path
        setattr(self, f"{name}_dir", full_path)
        full_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"{name.capitalize()} directory: {full_path}")
        logger.info(f"{name.capitalize()} directory purpose: {info['purpose']}")

    def _initialise_database(self, delete_existing_db=True):
        db_config = self.config['database']
        db_path = self.project_dir / db_config['path'].format(experiment_type=self.experiment_type)
        self.DB_FILE_PATH = db_path
        
        if delete_existing_db and db_path.exists():
            db_path.unlink()
            logger.info(f"Existing database file deleted: {db_path}")
        
        logger.info(f"Database file path: {db_path}")
        logger.info(f"Database purpose: {db_config['purpose']}")

    def setup_database(self):
        if self._db_connection is None:
            self._db_connection = duckdb.connect(str(self.DB_FILE_PATH))
            logger.info(f"Connected to database: {self.DB_FILE_PATH}")
        else:
            logger.info("Database connection already exists")

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
            conn.commit()

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

    def get_project_dir(self):
        return self.project_dir

    def get_config(self):
        return self.config

    def export_data_to_csv(self, df, filepath, info_message=None, header=None, log_relative_path=True):
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

    def create_markdown_link(self, file_path, link_text=None):
        file_path = Path(file_path).resolve()  # Get the absolute path
        project_root = self.project_dir.resolve()
        notebooks_dir = project_root / 'notebooks'
        cwd = Path.cwd().resolve()

        # Try to make the path relative to notebooks, project root, or cwd
        for base_path in [notebooks_dir, project_root, cwd]:
            try:
                link_path = file_path.relative_to(base_path)
                break
            except ValueError:
                continue
        else:
            # If we can't make it relative, use the absolute path
            link_path = file_path

        if not file_path.exists():
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        # For display, always make the path relative to the current working directory if possible
        try:
            display_path = file_path.relative_to(cwd)
        except ValueError:
            display_path = file_path

        if link_text is None:
            link_text = str(display_path)

        # Encode the link path to handle spaces and special characters
        encoded_link_path = urllib.parse.quote(str(link_path))

        markdown_link = f"[{link_text}]({encoded_link_path})"

        debug_info = {
            "current_dir": str(cwd),
            "project_root": str(project_root),
            "notebooks_dir": str(notebooks_dir),
            "full_path": str(file_path),
            "link_path": str(link_path),
            "encoded_link_path": encoded_link_path,
            "display_path": str(display_path),
            "file_path_input": str(file_path)
        }

        display(Markdown(markdown_link))
        #print(f"Debug info: {debug_info}")  # Use print for debug info
        return markdown_link, debug_info
    
    def export_database_tables(self, output_subdir, output_format="xlsx"):
            output_dir = self.output_dir / output_subdir
            output_dir.mkdir(parents=True, exist_ok=True)
            
            con = self.get_db_connection()
            
            try:
                tables = con.sql("SHOW TABLES;").fetchall()

                if output_format == "xlsx":
                    # Write to one Excel file by sheet name
                    excel_path = output_dir / "all_tables.xlsx"
                    with pd.ExcelWriter(excel_path) as writer:
                        for table in tables:
                            table_name = table[0]
                            # Query the table and convert it to a pandas DataFrame
                            df = con.table(table_name).to_df()
                            df.to_excel(writer, sheet_name=table_name, index=False)
                    logger.info(f"Exported database tables to: {excel_path}")
                    self.create_markdown_link(excel_path)

                elif output_format in ["csv", "parquet"]:
                    for table in tables:
                        table_name = table[0]
                        # Query the table and convert it to a pandas DataFrame
                        df = con.table(table_name).to_df()

                        if output_format == "csv":
                            # Write to a CSV file
                            csv_path = output_dir / f"{table_name}.csv"
                            df.to_csv(csv_path, index=False)
                            logger.info(f"Exported database table to: {csv_path}")
                            self.create_markdown_link(csv_path)
                        elif output_format == "parquet":
                            # Write to a Parquet file
                            parquet_path = output_dir / f"{table_name}.parquet"
                            df.to_parquet(parquet_path, index=False)
                            logger.info(f"Exported database table to: {parquet_path}")
                            self.create_markdown_link(parquet_path)

                else:
                    raise ValueError(f"Unsupported output format: {output_format}")
            except Exception as e:
                logger.error(f"Error exporting database tables: {e}")



    def display_file_with_highlighting(self, relative_path):
        full_path = self.project_dir / relative_path
        with open(full_path, 'r') as file:
            content = file.read()
        lexer = get_lexer_for_filename(full_path)
        formatter = HtmlFormatter(style='friendly')
        highlighted = highlight(content, lexer, formatter)
        display(HTML(f'<style>{formatter.get_style_defs()}</style>{highlighted}'))

# Usage example
# if __name__ == "__main__":
#     project = Project(experiment_type="RPE", table_page_length=20)
#     print(project.get_project_dir())
#     print(project.data_dir)
#     print(project.sql_dir)
#     print(project.DB_FILE_PATH)