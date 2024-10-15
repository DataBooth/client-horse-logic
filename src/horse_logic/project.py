import sys
from contextlib import contextmanager
from pathlib import Path

import duckdb
import itables.options as opt
import yaml
from IPython.display import Markdown, display
from itables import init_notebook_mode
from loguru import logger


class Project:
    def __init__(self, config_file='project_config.yaml', experiment_type=None, table_page_length=10):
        self.project_dir = self._find_project_root()
        self.config = self.load_config(config_file)
        self.experiment_type = experiment_type
        self._db_connection = None
        self._initialise_logger()
        self._initialise_itables(table_page_length)
        self._initialise_directories()
        self._initialise_database()
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

    def _initialise_database(self):
        db_config = self.config['database']
        db_path = self.project_dir / db_config['path'].format(experiment_type=self.experiment_type)
        self.DB_FILE_PATH = db_path
        logger.info(f"Database file path: {db_path}")
        logger.info(f"Database purpose: {db_config['purpose']}")
        self.setup_database(str(db_path))

    def setup_database(self, db_path):
        self._db_connection = duckdb.connect(db_path)
        logger.info(f"Connected to database: {db_path}")

    def get_db_connection(self):
        if self._db_connection is None:
            self.setup_database(str(self.DB_FILE_PATH))
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
        file_path = Path(file_path)
        project_root = self.get_project_dir()
        notebooks_dir = project_root / 'notebooks'
        cwd = Path.cwd()

        # Check if the current working directory is within the notebooks directory
        if notebooks_dir in cwd.parents or cwd == notebooks_dir:
            # If so, make the link relative to the notebooks directory
            try:
                link_path = file_path.relative_to(notebooks_dir)
            except ValueError:
                # If the file is not within the notebooks directory, fall back to project root
                link_path = file_path.relative_to(project_root)
        else:
            # If not in notebooks directory, make the link relative to the project root
            link_path = file_path.relative_to(project_root)

        # For display, always make the path relative to the current working directory
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
            "notebooks_dir": str(notebooks_dir),
            "full_path": str(full_path),
            "link_path": str(link_path),
            "display_path": str(display_path),
            "file_path_input": str(file_path)
        }

        display(Markdown(markdown_link))
        #logger.debug(f"Markdown link debug info: {debug_info}")
        return markdown_link, debug_info

# Usage example
# if __name__ == "__main__":
#     project = Project(experiment_type="RPE", table_page_length=20)
#     print(project.get_project_dir())
#     print(project.data_dir)
#     print(project.sql_dir)
#     print(project.DB_FILE_PATH)