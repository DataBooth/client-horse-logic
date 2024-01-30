import os
from pathlib import Path

import streamlit as st
from app_config import AppConfig
from database_connection import DatabaseConnection
from query_store import QueryStore
from tabs import TabDatasource, TabSchema, TabSQL, TabStats
import getpass

APP_NAME = "Horse Logic - Analytics App"
APP_CONFIG_PATH = "app/app_settings.toml"
DEPLOY_DOCKER_APP_USER = "appuser"
APP_LOGO = "app/1697_HL_HorseLogic_logo_colour_800px.png"


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

    # Initialize session state keys
    if 'login_attempted' not in st.session_state:
        st.session_state['login_attempted'] = False
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    # Check if the user is already authenticated
    if not st.session_state['authenticated']:
        if st.sidebar.button("Login") or st.session_state['login_attempted']:
            if username == "admin" and password == admin_password:
                st.session_state['authenticated'] = True
                st.session_state['login_attempted'] = False  # Reset login_attempted state
            else:
                st.session_state['login_attempted'] = True  # Set login_attempted state
                st.sidebar.error("Incorrect username or password")
    else:
        st.success("You are logged in.")

def get_admin_password():
    current_user = getpass.getuser()
    if current_user != DEPLOY_DOCKER_APP_USER:
        admin_password = st.secrets["authenticate"]["password"]
    else:
        admin_password = os.environ.get("ADMIN_PASSWORD", "ADMIN_PASSWORD_UNDEFINED")

    # If admin_password is not defined properly, raise an error
    if admin_password == "ADMIN_PASSWORD_UNDEFINED":
        error_message = f"Admin password is undefined. Current user is: {current_user}"
        raise EnvironmentError(error_message)
    else:
        return admin_password

def main_authenticated(ui_config):
    if Path(APP_LOGO).exists():
        st.sidebar.image(APP_LOGO)
    st.sidebar.header(APP_NAME)


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


def render_markdown_file(md_file_path):
    md_path = Path(md_file_path)
    try:
        with open(md_path, "r", encoding="utf-8") as md_file:
            markdown_content = md_file.read()
            st.markdown(markdown_content, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"The file {md_path.as_posix()} was not found.")
    except Exception as e:
        st.error(f"An error occurred while loading the file: {e}")


def main():
    st.set_page_config(page_title=APP_NAME, layout="wide")

    ui_config, datasource = load_app_config()

    db_conn = DatabaseConnection(datasource)
    if "db_conn" not in st.session_state:
        st.session_state["db_conn"] = db_conn

    if "data_choice" not in st.session_state:
        st.session_state["data_choice"] = db_conn.tables[0]

    admin_password = get_admin_password()

    ### Main UI

    # Very basic user authentication

    # Check user is authenticated
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False  # User is not authenticated by default

        st.header(APP_NAME)
        render_markdown_file(Path.cwd() / "app/md/info.md")
        if Path(APP_LOGO).exists():
            st.sidebar.image(APP_LOGO)

    # If not authenticated, show the login form
    if not st.session_state["authenticated"]:
        login_form(admin_password)
    else:
        main_authenticated(ui_config)


if __name__ == "__main__":
    main()
