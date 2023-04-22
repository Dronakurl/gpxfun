""" 
A plotly-dash app for analyzing gpx data of regular routes
"""
import logging

from dash import Dash

import dash_bootstrap_components as dbc  # pyright: ignore
from dash_app.app_layout import serve_layout
import callbacks  # pyright: ignore
from utils.mylog import get_log  # pyright: ignore

log = get_log("gpxfun", logging.DEBUG)

from dash_app.plots import TEMPLATE

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.css"
dashapp = Dash(__name__, external_stylesheets=[eval("dbc.themes." + TEMPLATE.upper()), dbc_css])
dashapp.title = "Bike route analyzer"

dashapp.layout = serve_layout


app = dashapp.server
app.secret_key = "super secret key"  # pyright: ignore

if __name__ == "__main__":
    # The host parameter is needed, so the app is also accessible
    # from another computer in the local network
    dashapp.run_server(debug=True, port=8080, host="0.0.0.0")

# start with: gunicorn app:app -b :8000
# start testing servier with: poetry run python -m app
