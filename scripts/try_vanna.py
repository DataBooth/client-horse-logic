from vanna.remote import VannaDefault

vn = VannaDefault(model="chinook", api_key="b9739d24b671490aa0169073a51b2821")
vn.connect_to_sqlite("https://vanna.ai/Chinook.sqlite")
vn.ask("What are the top 10 artists by sales?")

from vanna.streamlit import VannaStreamlitApp

VannaStreamlitApp(vn).run()

# from vanna.flask import VannaFlaskApp
# VannaFlaskApp(vn).run()
