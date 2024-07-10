import os
import duckdb
import toml
import httpx


class DuckDBManager:
    """
    A class to manage DuckDB connections (including MotherDuck) and execute SQL commands.
    """

    def __init__(self, db_path, secrets_file=None, logger=None, dry_run=False):
        """
        Initialise the DuckDBManager with a database path, secrets file, logger, and dry_run option.
        """
        self.db_path = db_path
        self.secrets_file = secrets_file
        self.logger = logger
        self.dry_run = dry_run
        self.conn = None
        if self.dry_run:
            self.logger.info("Dry run mode: SQL commands will not be executed just echoed to stdout.")

        if secrets_file:
            self.load_secrets(secrets_file)

        self.is_md_extension_loaded = False

    def load_motherduck_extension(self):
        if not self.is_md_extension_loaded:
            self.execute_sql("ATTACH 'md';")
            self.is_md_extension_loaded = True

    def load_secrets(self, secrets_file):
        """
        Load secrets from a file and set the motherduck_token environment variable.
        """
        try:
            secrets = toml.load(secrets_file)
            os.environ["motherduck_token"] = secrets["MD_TOKEN"]
            self.logger.info(f"Secrets loaded from {secrets_file} and environment variable set")
        except Exception as e:
            self.logger.error(f"Failed to load secrets: {e}")
            raise

    def connect(self):
        """
        Establish a connection to the database.
        """
        try:
            if self.db_path.startswith("md:") and "motherduck_token" not in os.environ:
                raise ValueError(
                    "No secrets file provided and motherduck_token environment variable not set."
                )
            self.conn = duckdb.connect(self.db_path)
            self.logger.info(f"Connected to {self.db_path}")

            if self.db_path.startswith("md:"):
                self.is_md_extension_loaded = True  # Extension is auto-loaded if a connection is made to MotherDuck

        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise

    def copy_ddb_to_motherduck(self, local_db_path, remote_db_name=None, dry_run=True):
        """
        Copy a local DuckDB database to the MotherDuck server.
        """
        try:
            self.load_motherduck_extension()
            self.logger.info(f"Local DB: {local_db_path}")
            self.execute_sql(f"DROP DATABASE IF EXISTS {remote_db_name};", dry_run=dry_run)
            self.execute_sql(
                f"CREATE OR REPLACE DATABASE {remote_db_name} FROM CURRENT_DATABASE();", dry_run=dry_run
            )

            if not dry_run:
                self.logger.info(f"Created database {remote_db_name} on https://motherduck.com")

            return remote_db_name
        except Exception as e:
            self.logger.error(f"Failed to copy local database to MotherDuck server: {e}")
            raise

    def execute_sql(self, command, *args, **kwargs):
        """
        Execute an SQL command, or print it if dry_run is True.
        """
        if self.dry_run:
            self.logger.info(f"ECHO only - SQL: {command}")
        else:
            try:
                result = self.conn.execute(command, *args, **kwargs)
                self.logger.info(f"ECHO - Executed SQL command: {command}")
                return result
            except Exception as e:
                self.logger.error(f"Failed to execute SQL command: {e}")
                raise

    def get_motherduck_ui_version(self):
        """
        Fetch the version of the MotherDuck UI.
        """
        try:
            with httpx.Client() as client:
                response = client.get("https://app.motherduck.com/version")
                response.raise_for_status()
                version_info = response.json()
                self.logger.info(f"MotherDuck UI version: {version_info['version']}")
                return version_info["version"]
        except Exception as e:
            self.logger.error(f"Failed to fetch MotherDuck UI version: {e}")
            raise

    def get_motherduck_db_version(self):
        """
        Fetch the version of the MotherDuck DuckDB.
        """
        try:
            self.load_motherduck_extension()
            version_info = self.execute_sql("PRAGMA md_version;")
            self.logger.info(f"MotherDuck DuckDB version: {version_info}")
            return version_info.fetchall()
        except Exception as e:
            self.logger.error(f"Failed to fetch MotherDuck DuckDB version: {e}")
            raise

    def __str__(self):
        """
        Return a user-friendly string representation of the DuckDBManager.
        """
        return f"DuckDBManager(db_path={self.db_path}, dry_run={self.dry_run})"

    def __repr__(self):
        """
        Return a developer-friendly string representation of the DuckDBManager.
        """
        return f"DuckDBManager(db_path={self.db_path}, secrets_file={self.secrets_file}, logger={self.logger}, dry_run={self.dry_run})"

    def __enter__(self):
        """
        Context management protocol method to establish a connection when entering the context.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context management protocol method to close the connection when exiting the context.
        """
        if self.conn:
            self.conn.close()
            self.logger.info(f"Closed connection to {self.db_path}")
