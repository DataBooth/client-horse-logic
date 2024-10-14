import csv
from rich.console import Console
from pynput.keyboard import Key, Listener
import duckdb

# Initialize Rich console for logging
console = Console()


class ExperimentControl:
    def __init__(self):
        self.console = Console()
        self.subjects = self.load_subjects("subjects.csv")
        self.db_conn = duckdb.connect("experiment_data.duckdb")
        self.setup_database()

    def load_subjects(self, filepath):
        """Load subjects from a CSV file."""
        subjects = {}
        with open(filepath, mode="r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                subjects[int(row["SubjectID"])] = row["SubjectName"]
        return subjects

    def setup_database(self):
        """Setup the DuckDB database schema."""
        self.db_conn.execute(
            "CREATE TABLE trials (TrialID INTEGER, SubjectID INTEGER, DayNumber INTEGER, TrialNumber INTEGER, Timestamp TIMESTAMP, RestartFlag BOOLEAN, Comment VARCHAR)"
        )
        self.db_conn.execute(
            "CREATE TABLE events (EventID INTEGER, TrialID INTEGER, EventType VARCHAR, Description VARCHAR, Timestamp TIMESTAMP)"
        )

    def start_experiment(self):
        """Main method to start the experiment."""
        self.console.print("Starting the experiment...", style="bold green")
        # Example of subject validation
        subject_id = 1  # Example subject ID
        if subject_id in self.subjects:
            self.console.print(
                f"Subject validated: [bold]{self.subjects[subject_id]}[/bold]", style="bold cyan"
            )
        else:
            self.console.print("Subject ID not found.", style="bold red")

        # This is where you would continue with the experiment flow

    def log_event(self, description, event_type="info", trial_id=None):
        """Log an event to the console and database."""
        self.console.print(description, style="bold yellow")
        # Log to database (simplified example)
        self.db_conn.execute(
            "INSERT INTO events (TrialID, EventType, Description, Timestamp) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            (trial_id, event_type, description),
        )

    # Additional methods for handling virtual buttons, trials, etc.
