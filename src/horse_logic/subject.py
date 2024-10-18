import pandas as pd
from pathlib import Path
from loguru import logger
from IPython.display import display, Markdown


class Subject:
    def __init__(self, project):
        self.project_dir = project.get_project_dir()
        self.config = project.get_config()["subject"]

    def get_subject_info(self):
        cohort_data_path = self.project_dir / Path(self.config["cohort_data"]["path"])

        if cohort_data_path.exists():
            subject_df = pd.read_excel(cohort_data_path)
            logger.info(f"Loaded subject info from: {cohort_data_path}")

            subject_df.rename({"No": "subject_number", "Horse": "subject_name", "Direction": "direction"}, axis=1, inplace=True)
            subject_df["subject_name"] = subject_df["subject_name"].str.lower()
            subject_df["direction"] = subject_df["direction"].str.upper()

            sorted_subjects = sorted(subject_df["subject_name"].to_list())
            subject_list = self._format_subject_list(sorted_subjects)

            logger.info(f"Subject count: {len(sorted_subjects)}")
            logger.info(f"Sorted subject names:\n{subject_list}")

            return subject_df
        else:
            logger.error(f"Subject info file not found: {cohort_data_path}")
            return None

    def _format_subject_list(self, subjects, width=115, indent="\t"):
        formatted_list = indent
        line_length = len(indent)
        for subject in subjects:
            if line_length + len(subject) + 2 > width:  # +2 for ", "
                formatted_list += "\n" + indent
                line_length = len(indent)
            formatted_list += subject + ", "
            line_length += len(subject) + 2
        return formatted_list.rstrip(", ")  # Remove trailing comma and space

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
                display(
                    Markdown(f"### {n_subject+1}. {subject_name.capitalize()}: {n_session} session(s)")
                )
                display(df_)
        return pd.DataFrame(session_summary, columns=["Subject number", "Subject name", "Session count"])
