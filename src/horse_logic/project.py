import functools
import sys
import textwrap
import urllib.parse
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import duckdb
import git
import itables.options as opt
import pandas as pd
import sqlparse
import yaml
from IPython.display import HTML, Markdown, display
from itables import init_notebook_mode
from loguru import logger
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename


class Project:
    def __init__(
        self,
        config_file="project_config.yaml",
        experiment_type=None,
        table_page_length=10,
        delete_existing_db=True,
    ):
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
        while current_dir.name != "notebooks":
            if (current_dir / "project_config.yaml").exists():
                return current_dir
            current_dir = current_dir.parent
        return current_dir.parent  # Return the parent of 'notebooks'

    def load_config(self, config_file):
        config_path = self.project_dir / config_file
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def _initialise_logger(self):
        logger.remove()  # Remove default handler
        logger.add(sys.stderr, format="<level>{level: <8}</level> | <level>{message}</level>")

    def _initialise_itables(self, table_page_length=10):
        init_notebook_mode(all_interactive=True, connected=False)
        opt.pageLength = table_page_length

    def _initialise_directories(self):
        for name, info in self.config["directories"].items():
            self.initialise_dir(name, info)

    def initialise_dir(self, name, info):
        if isinstance(info["path"], dict):
            # If path is a dict, assume it contains experiment-specific paths
            if self.experiment_type not in info["path"]:
                raise ValueError(
                    f"No path defined for experiment type '{self.experiment_type}' in directory '{name}'"
                )
            path = info["path"][self.experiment_type]
        else:
            # If path is a string, use it directly
            path = info["path"]

        full_path = self.project_dir / path
        setattr(self, f"{name}_dir", full_path)
        full_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"{name.capitalize()} directory: {full_path}")
        logger.info(f"{name.capitalize()} directory purpose: {info['purpose']}")

    def _initialise_database(self, delete_existing_db=True):
        db_config = self.config["database"]
        db_path = self.project_dir / db_config["path"].format(experiment_type=self.experiment_type)
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
            logger.info(f"DuckDB version: {self.get_duckdb_version()}")
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

    def run_multiple_queries(self, sql: str):
        """
        Execute multiple SQL queries and display the results in Jupyter.

        Args:
            sql (str): A semicolon-separated string of SQL queries to execute.

        Raises:
            ValueError: If no valid queries are found in the input string.

        This method splits the input SQL string into individual queries, executes each one,
        and displays the query along with its results. If a query fails, an error message
        will be displayed instead of the results. Each query is numbered for clarity.
        """
        queries = [q.strip() for q in sql.split(";") if q.strip()]

        if not queries:
            raise ValueError("No valid queries found in the input string.")

        conn = self.get_db_connection()

        for n_query, query in enumerate(queries, 1):
            try:
                display(Markdown(f"#### Query {n_query}:"))
                display(Markdown(f"```sql\n{query}\n```"))

                result = conn.sql(query).df()

                if result.empty:
                    display(Markdown("*No results found*"))
                else:
                    display(result)
            except Exception as e:
                display(Markdown(f"**Error executing query {n_query}:**"))
                display(Markdown(f"```\n{str(e)}\n```"))
            finally:
                display(Markdown("---"))  # Add a separator between queries

    def get_duckdb_version(self):
        """
        Get the version of DuckDB being used.

        Returns:
            str: The version of DuckDB.
        """
        try:
            conn = self.get_db_connection()
            version_query = "SELECT version();"
            result = conn.execute(version_query).fetchone()
            return str(result[0]) if result else "Unable to retrieve DuckDB version"
        except Exception as e:
            return f"Error retrieving DuckDB version: {str(e)}"

    def close_db_connection(self):
        if self._db_connection:
            self._db_connection.close()
            self._db_connection = None
            logger.info("Database connection closed")

    def list_database_objects(self, sort_by="alphabetical"):
        con = self.get_db_connection()

        # Get list of tables and views
        objects = con.sql(
            """
            SELECT table_name as name, table_type as type
            FROM information_schema.tables
            WHERE table_schema = 'main'
            ORDER BY table_name
        """
        ).fetchall()

        # Get object sizes and creation order
        object_info = []
        dependencies = defaultdict(list)
        for i, (name, obj_type) in enumerate(objects):
            # Get row count
            row_count = con.sql(f"SELECT COUNT(*) FROM {name}").fetchone()[0]

            # Get column count
            col_count = con.sql(
                f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name = '{name}'"
            ).fetchone()[0]

            # Check for dependencies (only for views)
            if obj_type.lower() == "view":
                view_definition = con.sql(
                    f"SELECT sql FROM sqlite_master WHERE name = '{name}'"
                ).fetchone()[0]
                for other_name, _ in objects:
                    if other_name != name and other_name.lower() in view_definition.lower():
                        dependencies[name].append(other_name)

            object_info.append(
                {
                    "name": name,
                    "type": obj_type,
                    "rows": row_count,
                    "columns": col_count,
                    "creation_order": i,
                    "dependencies": dependencies[name],
                }
            )

        # Sort objects
        if sort_by == "creation":
            object_info.sort(key=lambda x: x["creation_order"])
        else:  # alphabetical
            object_info.sort(key=lambda x: x["name"])

        # Format and display results
        print(f"{'Name':<30} {'Type':<15} {'Size':<15} {'Dependencies'}")
        print("-" * 80)
        for obj in object_info:
            size = f"{obj['rows']} x {obj['columns']}"
            deps = ", ".join(obj["dependencies"]) if obj["dependencies"] else "None"
            print(f"{obj['name']:<30} {obj['type']:<15} {size:<15} {deps}")

        # return object_info

    def drop_all_views(self):
        con = self.get_db_connection()

        # Get the DROP VIEW statements
        drop_statements = con.sql(
            """
            SELECT 'DROP VIEW IF EXISTS ' || table_name || ';' AS drop_statement
            FROM information_schema.tables
            WHERE table_schema = 'main' AND table_type = 'VIEW';
        """
        ).fetchall()

        # Execute each DROP VIEW statement
        for statement in drop_statements:
            con.sql(statement[0])

        print(f"Dropped {len(drop_statements)} views.")

    def drop_all_tables_except_defaults(
        self, default_tables=["ExperimentCBs", "TrialCBs", "ResponseCBs", "EventCBs"]
    ):
        con = self.get_db_connection()

        # Get all tables
        all_tables = con.sql(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'main' AND table_type = 'BASE TABLE'
        """
        ).fetchall()

        # Generate DROP TABLE statements for non-default tables
        drop_statements = [
            f"DROP TABLE IF EXISTS {table[0]};" for table in all_tables if table[0] not in default_tables
        ]

        # Execute each DROP TABLE statement
        for statement in drop_statements:
            con.sql(statement)

        print(f"Dropped {len(drop_statements)} non-default tables.")

    def __del__(self):
        self.close_db_connection()

    def get_project_dir(self):
        return self.project_dir

    def get_config(self):
        return self.config

    def export_data(
        self, df, filepath, export_type, info_message=None, log_relative_path=True, include_header=False
    ):
        filepath = Path(filepath)

        if export_type == "csv":
            df.to_csv(filepath, index=True, header=include_header)
        elif export_type == "xlsx":
            df.to_excel(filepath, index=False)
        else:
            raise ValueError(f"Unsupported export type: {export_type}")

        if log_relative_path:
            try:
                relative_path = filepath.relative_to(Path.cwd())
                path_info = f"Relative path: {relative_path}"
            except ValueError:
                path_info = f"Absolute path: {filepath}"
        else:
            path_info = f"Path: {filepath}"

        log_message = f"{len(df)} rows exported to {export_type.upper()}."  # {path_info}"
        if info_message:
            log_message = f"{info_message}. {log_message}"

        logger.info(log_message)

        if filepath.exists():
            self.create_markdown_link(filepath)
        else:
            logger.warning(f"File not found: {filepath}. Markdown link not created.")

    def export_data_to_csv(
        self, df, filepath, info_message=None, log_relative_path=True, include_header=False
    ):
        self.export_data(df, filepath, "csv", info_message, log_relative_path)

    def export_data_to_xlsx(
        self, data, filepath, sheet_names=None, info_message=None, log_relative_path=True
    ):
        filepath = Path(filepath)

        if not isinstance(data, list):
            data = [data]

        if sheet_names and len(sheet_names) != len(data):
            raise ValueError("Number of sheet names must match number of DataFrames")

        with pd.ExcelWriter(filepath) as writer:
            for i, df in enumerate(data):
                sheet_name = sheet_names[i] if sheet_names else f"Sheet{i+1}"
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        total_rows = sum(len(df) for df in data)
        log_message = f"{total_rows} total rows exported to XLSX across {len(data)} sheets."

        if log_relative_path:
            try:
                relative_path = filepath.relative_to(Path.cwd())
                path_info = f"Relative path: {relative_path}"
            except ValueError:
                path_info = f"Absolute path: {filepath}"
        else:
            path_info = f"Path: {filepath}"

        if info_message:
            log_message = f"{info_message}. {log_message}"

        logger.info(log_message)

        if filepath.exists():
            self.create_markdown_link(filepath)
        else:
            logger.warning(f"File not found: {filepath}. Markdown link not created.")

    def create_markdown_link(self, file_path, link_text=None, debug=False):
        file_path = Path(file_path).resolve()  # Get the absolute path
        project_root = self.project_dir.resolve()
        notebooks_dir = project_root / "notebooks"
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
            "file_path_input": str(file_path),
        }

        display(Markdown(markdown_link))
        if debug:
            print(f"Debug info: {debug_info}")  # Use print for debug info
        return markdown_link

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

    def low_cardinality_report(self, table_name, max_cardinality=5, export=True):
        con = self.get_db_connection()
        
        # First, get the column names
        columns_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
        columns = con.execute(columns_query).df()['column_name'].tolist()
        
        # Then, for each column, count distinct values
        results = []
        for column in columns:
            query = f"""
            SELECT 
                '{column}' AS column_name,
                -- COUNT(DISTINCT "{column}") AS distinct_count,
                -- STRING_AGG(DISTINCT CAST("{column}" AS VARCHAR), ', ') AS unique_values
                COUNT(DISTINCT CASE WHEN column_value IS NULL THEN 'NULL' 
                                    WHEN column_value = '' THEN 'EMPTY' 
                                    ELSE column_value END) AS distinct_count,
                STRING_AGG(DISTINCT CASE WHEN column_value IS NULL THEN 'NULL' 
                                        WHEN column_value = '' THEN 'EMPTY' 
                                        ELSE column_value END, ', ') AS unique_values
            FROM {table_name}
            """
            result = con.execute(query).df()
            if result['distinct_count'][0] <= max_cardinality:
                results.append(result)
        
        if not results:
            print(f"No columns with cardinality <= {max_cardinality} found in table '{table_name}'.")
            return None
        
        result_df = pd.concat(results, ignore_index=True)
        result_df = result_df.sort_values('distinct_count')
        
        display(Markdown(f"## Low Cardinality Report for '{table_name}'"))
        display(result_df)
        
        if export:
            filepath = self.output_dir / f"{table_name}_low_cardinality_report.xlsx"
            self.export_data_to_xlsx(result_df, filepath=filepath, 
                                    info_message=f"Exported low cardinality report for table: {table_name}")
        
        return result_df

    def view_and_export_table(self, table_name):
        con = self.get_db_connection()
        tables = con.sql("SHOW TABLES;").fetchall()
        if table_name in [table[0] for table in tables]:
            df = con.sql(f"SELECT * FROM {table_name}").df()
            filepath = self.output_dir / f"{table_name}.xlsx"
            self.export_data_to_xlsx(df, filepath=filepath, info_message=f"Exported table: {table_name}")
            display(Markdown(f"### Table: {table_name}"))
            display(df)
            
            # Generate and display low cardinality report
            low_card_df = self.low_cardinality_report(table_name, export=False)
            if low_card_df is not None and not low_card_df.empty:
                display(Markdown("### Low Cardinality Columns"))
                display(low_card_df)
        else:
            print(f"Table '{table_name}' does not exist in the database.")


    def view_and_export_sql(self, sql_query, output_name):
        con = self.get_db_connection()
        try:
            # Execute the SQL query
            df = con.sql(sql_query).df()
            
            # Export the results to an Excel file
            filepath = self.output_dir / f"{output_name}.xlsx"
            self.export_data_to_xlsx(df, filepath=filepath, info_message=f"Exported query results: {output_name}")
            
            # Display the results
            display(Markdown(f"### Query Results: {output_name}"))
            #display(df)
            
            return df  # Return the DataFrame for further use if needed
        
        except duckdb.Error as e:
            error_message = f"DuckDB Error: {str(e)}"
            display(Markdown(f"### Error in SQL Query"))
            display(Markdown(f"```sql\n{sql_query}\n```"))
            display(Markdown(f"**Error Message:** {error_message}"))
            return None
        
        except Exception as e:
            error_message = f"Unexpected Error: {str(e)}"
            display(Markdown(f"### Error in SQL Query"))
            display(Markdown(f"```sql\n{sql_query}\n```"))
            display(Markdown(f"**Error Message:** {error_message}"))
            return None
    
    def display_file_with_highlighting(self, relative_path):
        full_path = self.project_dir / relative_path
        with open(full_path, "r") as file:
            content = file.read()
        lexer = get_lexer_for_filename(full_path)
        formatter = HtmlFormatter(style="friendly")
        highlighted = highlight(content, lexer, formatter)
        display(HTML(f"<style>{formatter.get_style_defs()}</style>{highlighted}"))

    def sql_to_csv(self, csv_filename=None, purpose=None):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                nonlocal csv_filename
                # Generate a default filename if not provided
                if csv_filename is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")  # %S")
                    func_name = func.__name__
                    csv_filename = f"{func_name}_{timestamp}.csv"

                # Execute the original function with the project as the first argument
                result = func(self, *args, **kwargs)

                # Convert the result to a DataFrame if it's not already
                if not isinstance(result, pd.DataFrame):
                    result = pd.DataFrame(result)

                # Create a Path object for the CSV file in the output directory
                csv_path = self.output_dir / csv_filename

                # Ensure the output directory exists
                csv_path.parent.mkdir(parents=True, exist_ok=True)

                # Export the DataFrame to CSV
                result.to_csv(csv_path, index=False)

                # Format the SQL query
                formatted_query = sqlparse.format(args[0], reindent=True, keyword_case="upper")

                # Append the SQL query and purpose (if provided) as comments to the CSV file
                with open(csv_path, "a") as f:
                    f.write("\n\n")
                    if purpose:
                        f.write(f"/* Purpose:\n{textwrap.fill(purpose, width=80)}\n*/\n\n")
                    f.write("/* SQL Query:\n")
                    for line in formatted_query.split("\n"):
                        wrapped_lines = textwrap.wrap(line, width=80)
                        for wrapped_line in wrapped_lines:
                            f.write(f"{wrapped_line}\n")
                    f.write("*/\n")

                # Create a relative path for the file link
                relative_path = csv_path.relative_to(Path.cwd())

                # Display the DataFrame
                display(result)

                # Display a link to the CSV file
                display(
                    HTML(
                        f'<a href="{relative_path}" target="_blank">Click to download:  <code>{csv_path.name}</code></a><p></p>'
                    )
                )

                return result

            return wrapper

        return decorator


    def get_github_repo(self):
        try:
            
            repo = git.Repo(self.project_dir, search_parent_directories=True)
            remote_url = repo.remotes.origin.url
            
            # Extract the GitHub repo name from the remote URL
            if "github.com" in remote_url:
                # Handle SSH and HTTPS URLs
                if remote_url.startswith("git@github.com:"):
                    repo_name = remote_url.split(":")[1].rstrip(".git")
                else:
                    repo_name = remote_url.split("github.com/")[1].rstrip(".git")
                
                return f"https://github.com/{repo_name}"
            else:
                return None
        except ImportError:
            logger.warning("GitPython is not installed. Unable to retrieve GitHub repository information.")
            return None
        except git.exc.InvalidGitRepositoryError:
            logger.info("The project directory is not a Git repository.")
            return None
        except Exception as e:
            logger.error(f"Error retrieving GitHub repository: {str(e)}")
            return None


# Usage example
# if __name__ == "__main__":
#     project = Project(experiment_type="RPE", table_page_length=20)
#     print(project.get_project_dir())
#     print(project.data_dir)
#     print(project.sql_dir)
#     print(project.DB_FILE_PATH)
