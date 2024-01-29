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


def main():
    st.set_page_config(page_title=APP_NAME, layout="wide")

    ui_config, datasource = load_app_config()

    db_conn = DatabaseConnection(datasource)
    if "db_conn" not in st.session_state:
        st.session_state["db_conn"] = db_conn

    if "data_choice" not in st.session_state:
        st.session_state["data_choice"] = db_conn.tables[0]

    ### Main UI

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
