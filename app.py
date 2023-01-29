""" 
A dash app to visualize the results
"""
# from dash import dcc, html, Dash, Output, Input, State, ctx, MATCH, ALL, dash_table
import base64
import io
import json
from pathlib import Path
import pickle
import re
import threading
from typing import Tuple
import uuid

from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
import dash_bootstrap_components as dbc
import pandas as pd

from calc_dist_matrix import mae, update_dist_matrix
from cluster_it import cluster_all
from infer_start_end import infer_start_end
from parse_gpx import update_pickle_from_folder
from plots import plotaroute, violin
from utilities import getfilelist

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.css"
dashapp = Dash(__name__, external_stylesheets=[dbc.themes.SLATE, dbc_css])
dashapp.title = "GPX analyzer"

header = html.H4(
    "GPX analyzer - What's the fastest way to get to work? ",
    style={"margin-top": "5px"}
    # className="bg-primary text-white p-2 mb-2 text-center",
)
uploadfield = dcc.Upload(
    id="upload-data",
    children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
    multiple=True,
    style={
        "height": "60px",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
        "margin": "10px",
    },
)
load_textarea = dcc.Textarea(
    id="load_textarea",
    value="",
    readOnly=True,
    rows=12,
    style={"width": "100%", "resize": "none", "padding": "5px"},
)
progessbar = dbc.Progress(value=25, id="progressbar")
loadcard = dbc.Card(
    [
        dbc.CardHeader("Upload data from gpx files"),
        dbc.CardBody([uploadfield, progessbar, load_textarea]),
    ]
)
loadstuff = dbc.Tab(loadcard, disabled=False, label="Load", tab_id="loadstuff")

showmaps = dbc.Tab(
    dbc.Card(
        [
            dbc.CardHeader("Map of important clusters"),
            dbc.CardBody(dcc.Graph(id="mapplot")),
        ]
    ),
    label="Clusters",
)

violinfactor_dropdown = dcc.Dropdown(
    options={
        "wochentag": "Wochentag",
        "cluster": "Cluster",
        "jahreszeit": "Jahreszeit",
    },
    value="cluster",
    id="violinfactor",
    style={
        "width": "179px",
        "margin-bottom": "5px",
        # "display": "inline",
    },
)
violinfactor_selected_file_txt = dcc.Textarea(
    id="violinfactor_selected_file_txt",
    value="Click on a data point to show filename",
    readOnly=True,
    rows=18,
    style={"width": "100%", "resize": "none", "padding": "5px"},
)
dataandcontrols = dbc.Card(
    [violinfactor_dropdown, violinfactor_selected_file_txt], body=True
)
violinplot = dcc.Graph(id="violinplot")
plotcard = (
    dbc.Card(
        [
            dbc.CardHeader("Plot for different factors"),
            dbc.CardBody([violinplot]),
        ]
    ),
)
violins = dbc.Tab(
    dbc.Row([dbc.Col(dataandcontrols, width=5), dbc.Col(plotcard, width=7)]),
    label="Violins",
    tab_id="violintab",
)


clusterinfo = dcc.Textarea(
    id="clusterinfo",
    value="",
    readOnly=True,
    rows=18,
    style={"width": "100%", "resize": "none", "padding": "5px"},
)
clusterpoints = [
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id="clustergraph1", style={"height": "200px"}), width=6),
            dbc.Col(dcc.Graph(id="clustergraph2", style={"height": "200px"}), width=6),
        ],
        className="h-50",
        # style={"background-color":"red"}
    ),
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id="clustergraph3", style={"height": "200px"}), width=6),
            dbc.Col(dcc.Graph(id="clustergraph4", style={"height": "200px"}), width=6),
        ],
        className="h-50",
        # style={"background-color":"green"}
    ),
]

clusterbody = dbc.Row(
    [
        dbc.Col(
            clusterinfo,
            width=3,
            # style={"background-color": "blue"}
        ),
        dbc.Col(clusterpoints, width=9),
    ]
)
clustertab = dbc.Tab(
    dbc.Card(
        [
            dbc.CardHeader("Determine start end points and common routes"),
            dbc.CardBody(clusterbody),
        ]
    ),
    label="Cluster routes",
    tab_id="clustertab",
)

tabs = dbc.Tabs([loadstuff, clustertab, showmaps, violins], active_tab="loadstuff")


def serve_layout():
    sessionid = str(uuid.uuid4())
    print(f"serve_layout: start with sessionid = {sessionid}")

    return dbc.Container(
        [
            header,
            tabs,
            dcc.Interval(id="progressinterval", disabled=False, interval=1000),
            dcc.Store(data=False, id="storedflag"),
            dcc.Store(data=sessionid, id="sessionid"),
            dcc.Store(data=0, id="numberoffiles"),
        ],
        fluid=True,
        className="dbc",
    )


dashapp.layout = serve_layout


@dashapp.callback(
    Output("progressbar", "value"),
    Output("storedflag", "data"),
    # Output("load_textarea", "value"),
    Input(
        "progressinterval", "n_intervals"
    ),  # each second, this Input triggers the callback
    State("sessionid", "data"),
    State("numberoffiles", "data"),
)
def update_progessbar(n_intervals, sessionid, numberoffiles):
    """update the progress bar from the number of files remaining"""
    if ctx.triggered_id == None or numberoffiles < 1:
        return (0, False)
    n = len(getfilelist(Path("sessions") / sessionid, "gpx"))
    storedflag = n == 0
    # check if the parsing thread is finished, otherwise, remain in state "not stored"
    for thread in threading.enumerate():
        print(f"update_progessbar({sessionid}): thread.names : {thread.name}")
        if thread.name == "read" and thread.is_alive():
            storedflag = False
    percentage = (numberoffiles - n) / numberoffiles * 100
    print(
        f"update_progessbar{sessionid}: numberoffiles={numberoffiles}, percentage={percentage}, storedflag={storedflag}"
    )
    return (percentage, storedflag)


def parse_and_cluster(
    infolder: str,
    mypickle: Path = Path("pickles/df.pickle"),
    delete: bool = False,
):
    df, updated = update_pickle_from_folder(
        infolder=infolder, mypickle=mypickle, delete=delete
    )
    df, most_imp_clusters = infer_start_end(df)
    with open(Path(mypickle).parents[0] / "most_imp_clusters.pickle", "wb") as f:
        pickle.dump(most_imp_clusters, f)
    # distance matrix is generated, if not already stored in a pickle
    dists = update_dist_matrix(
        df,
        mypickle=Path(mypickle).parents[0] / "dists.pickle",
        updated=updated,
        simmeasure="mae",
    )
    # Apply Cluster
    df = cluster_all(df, dists)
    with open(mypickle, "wb") as f:
        pickle.dump(df, f)


def get_data_from_pickle_session(sessionid: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    picklefn = Path("sessions") / sessionid / "df.pickle"
    if not picklefn.is_file():
        raise ValueError(f"pickle file {picklefn} doesn't exist!") 
    with open(picklefn, "rb") as f:
        df = pickle.load(f)
    with open(Path("sessions") / sessionid / "most_imp_clusters.pickle", "rb") as f:
        most_imp_clusters = pickle.load(f)
    return df, most_imp_clusters


@dashapp.callback(
    Output("numberoffiles", "data"),
    Input("upload-data", "contents"),
    Input("upload-data", "filename"),
    State("sessionid", "data"),
    prevent_initial_call=True,
)
def upload(contents, filenames, sessionid):
    """upload gpx data to session folder and start parsing thread"""
    if ctx.triggered_id == None:
        return
    # create sessionid folder
    (Path("sessions") / sessionid).mkdir(parents=True, exist_ok=True)
    # store alle files in a tmp session directory
    for ii in range(len(contents)):
        cc = contents[ii]
        filename = filenames[ii]
        _, content_string = cc.split(",")
        decoded = base64.b64decode(content_string)
        strdata = decoded.decode("utf-8")
        with open(Path("sessions") / sessionid / filename, "w") as f:
            f.write(strdata)
    print(f"upload({sessionid}): number of files = {len(contents)}")
    mythread = threading.Thread(
        target=parse_and_cluster,
        name="read",
        kwargs={
            "infolder": Path("sessions") / sessionid,
            "mypickle": Path("sessions") / sessionid / "df.pickle",
            "delete": True,
        },
    )
    mythread.start()
    return len(contents)


@dashapp.callback(
    Output("mapplot", "figure"),
    Output("clusterinfo", "value"),
    Input("storedflag", "data"),
    State("sessionid", "data"),
    prevent_initial_call=True,
)
def showmap(storedflag, sessionid):
    """Update the map with clusters"""
    if storedflag == False:
        return no_update
    dr, most_imp_clusters = get_data_from_pickle_session(sessionid)
    if type(dr) != pd.DataFrame:
        return no_update
    fig = plotaroute(
        dr,
        groupfield="cluster",
        title=None,
    )
    return fig, print(most_imp_clusters)


# @dashapp.callback(
#     Output("violinplot", "figure"),
#     Input("violinfactor", "value"),
#     Input("storedflag", "data"),
#     State("sessionid", "data"),
#     prevent_initial_call=True,
# )
# def showhists(violinfactor, storedflag, sessionid):
#     """Update the histogram or violin plots"""
#     if storedflag == False:
#         return no_update
#     dr = get_data_from_pickle_session(sessionid)
#     fig = violin(dr, violinfactor)
#     return fig


# @dashapp.callback(
#     Output("violinfactor_selected_file_txt", "value"),
#     Input("violinplot", "clickData"),
#     Input("storedflag", "data"),
#     State("sessionid", "data"),
#     prevent_initial_call=True,
# )
# def clickondata(clickdata, storedflag, sessionid):
#     """Show information on the clicked data point"""
#     if storedflag == False:
#         return no_update
#     dr = get_data_from_pickle_session(sessionid)
#     if clickdata is not None and storedflag:
#         # I don't know, why I need this, but the given clickdata is not a proper dict at first
#         clickeddict = json.loads(json.dumps(clickdata))
#         clicked_file = clickeddict["points"][0]["customdata"][0]
#         clickedseries = dr[dr["dateiname"] == clicked_file].iloc[0]
#         clickedseries = clickedseries.drop(["route", "route_inter"])
#         return "\n".join(f"{clickedseries}".split("\n")[0:-1])
#     else:
#         return "Click on a data point to show filename and infos"


app = dashapp.server
app.secret_key = "super secret key"

if __name__ == "__main__":
    dashapp.run_server(debug=True)

# start with: gunicorn app:app -b :8000
