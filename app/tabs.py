import re
import string
from pathlib import Path

import streamlit as st
from query_validation import QueryValidator


class TabDatasource:
    def __init__(self):
        self.db_conn = st.session_state["db_conn"]
        self.data_table_name = self.db_conn
        self.display()

    def display(self):
        if self.db_conn.datasource_info["type"] != "duckdb" and len(self.db_conn.tables) > 1:
            st.info(
                "Data files load complete: Choose data source below and then select SQL tab to create/run queries."
            )
        else:
            st.info("Data load complete: Select SQL tab to create/run queries.")

        report = "\n".join(f"- {table_report}" for table_report in self.db_conn.report["tables_created"])
        st.markdown(report)

        if self.db_conn.datasource_info["type"] == "duckdb":
            st.write(self.db_conn.datasource_info["paths"])
            if "data_choice" not in st.session_state:
                st.session_state["data_choice"] = self.db_conn.datasource_info["paths"]
        else:
            data_choice = st.selectbox(label="Choose data source:", options=self.db_conn.tables)
            st.session_state["data_choice"] = data_choice

    def create_data_connection(self, data_choice):
        if not Path(data_choice).exists():
            raise FileNotFoundError(f"The data source {(data_choice).as_posix()} was not found.")

        # Connect and create a table from the parquet file
        table_create_sql = f"CREATE OR REPLACE TABLE {self.data_table_name} AS SELECT * FROM read_parquet('{data_choice}');"
        self.db_conn.execute(table_create_sql)
        return self.db_conn.connection, table_create_sql


class TabStats:
    def __init__(self):
        self.db_conn = st.session_state["db_conn"]
        self.data_choice = st.session_state["data_choice"]

        st.markdown(f"`{self.data_choice}` - **Categorical fields:**")
        st.write(self.db_conn.query_df(f"SELECT * FROM {self.data_choice}").describe(include="object"))
        st.markdown("")
        st.markdown(f"`{self.data_choice}` - **Numeric fields:**")
        st.write(self.db_conn.query_df(f"SELECT * FROM {self.data_choice}").describe())


class TabSQL:
    def __init__(self):
        self.query_store = st.session_state["query_store"]
        self.db_conn = st.session_state["db_conn"]
        self.data_choice = st.session_state["data_choice"]
        self.display()

    def display(self):
        st.subheader(f"SQL Query: `{self.data_choice}`")
        # Option 1: User enters a query
        query_name = st.text_input("Query Name")
        query_description = st.text_area("Query Description")
        query_author = st.text_input("Author")
        sql_query = st.text_area("Enter your SQL query here:")
        execute_button = st.button("Execute Query")
        save_button = st.button("Save Query")

        if execute_button and sql_query:
            self.execute_and_optionally_save_query(
                sql_query, query_name, query_description, query_author, save_button
            )

        # Option 2: Upload a query from a .sql file
        uploaded_file = st.file_uploader("Upload your .sql file here...", type=["sql"])
        if uploaded_file is not None:
            sql_query_from_file = uploaded_file.getvalue().decode("utf-8")
            st.text_area("Uploaded SQL query:", value=sql_query_from_file, height=100)
            execute_uploaded_button = st.button("Execute Uploaded Query")
            save_uploaded_button = st.button("Save Uploaded Query")

            if execute_uploaded_button:
                self.execute_and_optionally_save_query(
                    sql_query_from_file,
                    query_name,
                    query_description,
                    query_author,
                    save_uploaded_button,
                )

        # Option 3: Select a saved query to run
        saved_queries = self.query_store.get_saved_queries_ordered_by_run_count()
        saved_query_names = [query[0] for query in saved_queries]
        selected_query_name = st.selectbox("Choose a saved query to run:", saved_query_names)
        run_saved_query_button = st.button("Run Saved Query")

        if run_saved_query_button and selected_query_name:
            selected_query = next(
                (query for query in saved_queries if query[0] == selected_query_name), None
            )
            if selected_query:
                self.execute_and_optionally_save_query(
                    selected_query[3],
                    selected_query[0],
                    selected_query[1],
                    selected_query[2],
                    False,
                )

    def execute_and_optionally_save_query(self, query_sql, name, description, author, save):
        # Remove non-printable characters
        printable = set(string.printable)
        query_sql = "".join(filter(lambda x: x in printable, query_sql))

        # Replace double quotes with single quotes
        query_sql = query_sql.replace('"', "'")

        # Remove unnecessary whitespace
        query_sql = re.sub(r"\s+", " ", query_sql).strip()

        # Ensure the query ends with a semicolon
        if not query_sql.endswith(";"):
            query_sql += ";"

        st.code(query_sql, language="sql")
        query_validator = QueryValidator("duckdb")

        is_valid, validation_message = query_validator.validate(query_sql)
        if is_valid:
            try:
                # Execute the query and display results
                result = self.db_conn.query_df(query_sql)
                st.write(result)
                self.query_store.increment_query_run_count(name)
                if save:
                    self.query_store.save_query(name, description, author, query_sql)
                    st.success("Query saved successfully.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.error(f"Query validation failed: {validation_message}")


class TabSchema:
    def __init__(self):
        self.db_conn = st.session_state["db_conn"]
        self.data_choice = st.session_state["data_choice"]
        self.display()

    def display(self):
        if self.db_conn.datasource_info["type"] == "database":
            st.subheader("Database Schema")
            schema_query = f"PRAGMA table_info('{self.data_choice}');"
        else:
            st.subheader(f"Table schema: `{self.data_choice}`")
            schema_query = f"PRAGMA table_info('{self.data_choice}');"
        try:
            schema_result = self.db_conn.query_df(schema_query)
            # st.write(schema_result)
            # schema_df = pd.DataFrame(
            #     schema_result,
            #     columns=[
            #         "Column ID",
            #         "Name",
            #         "Type",
            #         "Not Null",
            #         "Default Value",
            #         "Primary Key",
            #     ],
            # )
            st.dataframe(schema_result)
        except Exception as e:
            st.error(f"An error occurred while fetching the schema: {str(e)}")
