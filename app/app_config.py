import toml
from pathlib import Path


class AppConfig:
    def __init__(self, config_path="app_settings.toml"):
        self.config = toml.load(config_path)

    def get_ui_config(self):
        return self.config.get("ui", {})

    def get_querystore_path(self):
        return self.config.get("querystore", {})

    def get_datasource_path(self):
        datasource_config = self.config.get("datasource", {})
        path = datasource_config.get("path")
        if isinstance(path, str):
            return self._validate_single_path(path)
        elif isinstance(path, list):
            return self._validate_path_list(path)
        else:
            raise ValueError("The path should be a string or a list of strings.")

    def _validate_single_path(self, path):
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"ERROR: {file_path.as_posix()} not found.")

        if file_path.suffix in [".ddb", ".duckdb", ".sqlite"]:
            return {"type": "database", "path": file_path}
        else:
            raise ValueError("Unsupported database file type.")

    def _validate_path_list(self, paths):
        if not paths:
            raise ValueError("The path list is empty.")

        file_paths = [Path(p) for p in paths]
        file_types = {p.suffix.replace(".", "") for p in file_paths}

        if len(file_types) > 1:
            raise ValueError("All files in the list must have the same extension.")

        file_type = file_types.pop()
        if file_type not in ["parquet", "csv"]:
            raise ValueError("Unsupported file type in the list.")

        if len(file_paths) != len(set(file_paths)):
            raise ValueError("Duplicate filenames are not allowed.")

        not_found_files = [str(p) for p in file_paths if not p.exists()]
        if not_found_files:
            raise FileNotFoundError(f"The following files do not exist: {', '.join(not_found_files)}")

        return {"type": file_type, "paths": file_paths}
