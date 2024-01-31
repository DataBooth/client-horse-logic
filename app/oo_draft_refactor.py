# config.py
# This class handles loading and parsing the app_config.toml file
# and provides methods to retrieve configuration values.
import toml


class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_path, "r") as config_file:
            return toml.load(config_file)

    def get(self, key, default=None):
        return self.config.get(key, default)


# authentication.py
# This class encapsulates the logic related to user authentication.
import streamlit as st


class Authentication:
    def __init__(self, config):
        self.config = config

    def login_form(self):
        st.sidebar.title("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Login"):
            if self.authenticate(username, password):
                st.session_state["authenticated"] = True
            else:
                st.sidebar.error("Incorrect username or password")

    def authenticate(self, username, password):
        correct_username = self.config.get("authenticate")["username"]
        correct_password = self.config.get("authenticate")["password"]
        return username == correct_username and password == correct_password


# database.py
# This class handles all database-related operations.

import duckdb


class Database:
    def __init__(self, config):
        self.config = config
        self.connection = self.create_connection()

    def create_connection(self):
        db_path = self.config.get("database")["path"]
        return duckdb.connect(database=db_path)

    def execute_query(self, query):
        return self.connection.execute(query).fetchall()


# tabs.py
# Tab Base Class and Specific Tab Classes
# These remain as previously outlined, with each specific tab class
# inheriting from BaseTab and implementing its own render method.
class BaseTab:
    def __init__(self, name):
        self.name = name

    def render(self, tab):
        raise NotImplementedError("Subclasses should implement this method.")


class DatasourceTab(BaseTab):
    def render(self, tab):
        with tab:
            pass
            # Custom rendering code for the Datasource tab


class SchemaTab(BaseTab):
    def render(self, tab):
        with tab:
            # Custom rendering code for the Schema tab
            pass


# ... other specific tab classes


class TabManager:
    def __init__(self, config):
        self.config = config
        self.tabs = self.load_tabs()

    def load_tabs(self):
        tab_objects = []
        for tab_config in self.config["tabs"]["list"]:
            if tab_config["enabled"]:
                tab_class = globals().get(f"{tab_config['name']}Tab")
                if tab_class:
                    tab_objects.append(tab_class(tab_config["name"]))
        return tab_objects

    def render(self):
        tab_labels = [tab.name for tab in self.tabs]
        tabs = st.tabs(tab_labels)
        for i, tab in enumerate(self.tabs):
            tab.render(tabs[i])


# app.py
# This class encapsulates the entire application.
class App:
    def __init__(self):
        self.config = Config("app_config.toml")
        self.auth = Authentication(self.config)
        self.db = Database(self.config)
        self.tab_manager = TabManager(self.config)

    def run(self):
        if "authenticated" not in st.session_state:
            st.session_state["authenticated"] = False

        if not st.session_state["authenticated"]:
            self.auth.login_form()
        else:
            self.tab_manager.render()


if __name__ == "__main__":
    app = App()
    app.run()
