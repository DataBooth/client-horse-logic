import streamlit as st
from app_config import AppConfig
from database_connection import DatabaseConnection
from query_store import QueryStore
from tabs import TabDatasource, TabSchema, TabSQL, TabStats

APP_NAME = "Horse Logic - Logfile Query Tool"
APP_CONFIG_PATH = "app/app_settings.toml"


def load_app_config():
    app_config = AppConfig(APP_CONFIG_PATH)
    ui_config = app_config.get_ui_config()
    datasource = app_config.get_datasource_path()
    return ui_config, datasource

# Define a simple login form
def login_form(admin_password):
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "admin" and admin_password:  # Replace with your credentials
            st.session_state['authenticated'] = True
        else:
            st.sidebar.error("Incorrect username or password")


def main():
    st.set_page_config(page_title=APP_NAME, layout="wide")

    ui_config, datasource = load_app_config()

    db_conn = DatabaseConnection(datasource)
    if "db_conn" not in st.session_state:
        st.session_state["db_conn"] = db_conn

    if "data_choice" not in st.session_state:
        st.session_state["data_choice"] = db_conn.tables[0]

    user_password = st.secrets["authenticate"]["password"]


    ### Main UI

    # Very basic user authentication

    # Check user is authenticated
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False  # User is not authenticated by default

    # If not authenticated, show the login form
    if not st.session_state['authenticated']:
        login_form(user_password)
    else:
        # Your main app goes here
        st.header(APP_NAME)


        tab_datasource, tab_stats, tab_sql, tab_schema = st.tabs(ui_config["tabs"])


        with tab_datasource:
            TabDatasource()

        with tab_stats:
            TabStats()

        with tab_sql:
            query_store = QueryStore()
            if "query_store" not in st.session_state:
                st.session_state["query_store"] = query_store
            TabSQL()

        with tab_schema:
            TabSchema()


if __name__ == "__main__":
    main()
