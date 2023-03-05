""" 
A plotly-dash app for analyzing gpx data of regular routes
"""
from pathlib import Path
import logging
import pandas as pd
import plotly.express as px

from dash import html, dcc, Dash, Input, Output, State, ctx, no_update, MATCH, callback
import dash_bootstrap_components as dbc

from app_data_functions import  get_data_from_pickle_session
from app_layout import serve_layout
from mylog import get_log
from analyzer_factory import AnalyzerFactory
import callbacks  # pyright: ignore

log = get_log("gpxfun", logging.DEBUG)

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.css"
dashapp = Dash(__name__, external_stylesheets=[dbc.themes.VAPOR, dbc_css])
dashapp.title = "Bike route analyzer"

dashapp.layout = serve_layout


@dashapp.callback(
    Output("analyzer_dropdown", "options"),
    Output("analyzer_dropdown", "value"),
    Input("sessionid", "data"),
    prevent_initial_call=False,
)
def update_analyzer_dropdown(_):
    """Initialize the dropdown for the analyzer section from available stuff"""
    log.debug("CALLBACK update_analyzer_dropdown: " + str(ctx.triggered_id))
    af = AnalyzerFactory().get_available_analyzers()
    return af, af[0]


@dashapp.callback(
    Output("analyzeroptionscard", "children"),
    State("sessionid", "data"),
    Input("storedflag", "data"),
    Input("analyzer_dropdown", "value"),
    prevent_initial_call=True,
)
def update_analyzer_dropdown(sessionid, storedflag, analyzerid):
    """Initialize the dropdown for the route cluster using startendcluster"""
    log.debug("CALLBACK update_analyzer_dropdown: " + str(ctx.triggered_id))
    if storedflag == False:
        return no_update
    dr, _ = get_data_from_pickle_session(sessionid)
    # an = AnalyzerFactory(dr).get_analyzer(analyzerid=analyzerid)
    # return an.DashSettings(an)
    return no_update

    # Output("analyerresultscars","children"),

    # dbc.Button("save file",id={'type': 'savebutton', 'index':filename},color="primary")
    # Input({'type': 'savebutton', 'index': ALL}, 'n_clicks'),
    #     fn=ctx.triggered_id["index"]


app = dashapp.server
app.secret_key = "super secret key"  # pyright: ignore

if __name__ == "__main__":
    # The host parameter is needed, so the app is also accessible
    # from another computer in the local network
    dashapp.run_server(debug=True, host="0.0.0.0")

# start with: gunicorn app:app -b :8000
# start testing servier with: poetry run python -m app
