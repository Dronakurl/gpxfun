""" 
A plotly-dash app for analyzing gpx data of regular routes
"""
import logging

from dash import Dash, Input, MATCH, Output, State, callback, ctx, dcc, html, no_update
import dash_bootstrap_components as dbc

from analyzer_factory import AnalyzerFactory
from app_data_functions import get_data_from_pickle_session
from app_layout import serve_layout
import callbacks
from mylog import get_log  # pyright: ignore

log = get_log("gpxfun", logging.DEBUG)

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.css"
dashapp = Dash(__name__, external_stylesheets=[dbc.themes.VAPOR, dbc_css])
dashapp.title = "Bike route analyzer"

dashapp.layout = serve_layout




@callback(
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
