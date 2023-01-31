""" 
Layout for the dash app, to be used in the main app.py
"""
import uuid
from utilities import getdirlist

from dash import dcc, html
import dash_bootstrap_components as dbc


def getsessionids():
    opts = {}
    for sessionpath in getdirlist("sessions", withpath=True):
        opts[sessionpath.name] = sessionpath.name
    return opts


def get_header():
    return html.H4(
        [
            html.B("Bike route analyzer", style={"color": "#FF9800"}),
            html.Span(" - What's the fastest way from A to B? "),
        ],
        style={"margin-top": "5px", "text-align": "center"},
        className="bg-primary text-white p-2 mb-2 text-center",
    )


def get_loadstuff():
    uploadfield = dcc.Upload(
        id="upload-data",
        children=html.Div(["Drag and Drop or ", html.A("Select GPX Files")]),
        multiple=True,
        style={
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            # "borderStyle": "dashed",
            # "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px",
            "background-color": "#FF9800",
            "color": "black",
        },
    )
    load_textarea = dcc.Textarea(
        id="load_textarea",
        value="",
        readOnly=True,
        rows=3,
        style={
            "width": "100%",
            "resize": "none",
            "padding": "5px",
            "margin-top": "5px",
            # "display": "none",
        },
    )
    progessbar = dbc.Progress(
        value=0,
        id="progressbar",
        label="no files to load",
        color="#FF9800",
        style={"color": "black", "margin-bottom": "5px"},
    )
    startend_cluster_dropdown = dcc.Dropdown(
        options={
            "readdatafirst": "Load data first",
        },
        # value=["readdatafirst"],
        placeholder="select start/end combination",
        id="startend_cluster_dropdown",
        style={
            "width": "100%",
            "margin-bottom": "5px",
        },
        multi=True,
    )
    cluster_dropdown = dcc.Dropdown(
        options={
            "readdatafirst": "Load data first",
        },
        placeholder="select type of route",
        id="cluster_dropdown",
        style={
            "width": "100%",
            "margin-bottom": "5px",
        },
        multi=True,
    )
    opts = getsessionids()
    picksessionid = dcc.Dropdown(
        options=opts,
        placeholder="..or select data from sessionid",
        id="picksessionid",
        style={
            "width": "100%",
            "margin-bottom": "5px",
        },
    )
    dropdowncard = dbc.Card(
        [
            dbc.CardHeader("Select routes to analyze"),
            dbc.CardBody([ startend_cluster_dropdown, cluster_dropdown,]),
        ]
    )
    loadcard = dbc.Card(
        [
            dbc.CardHeader("Load GPX data"),
            dbc.CardBody([uploadfield, progessbar, picksessionid, load_textarea]),
            # dbc.CardBody([uploadfield, progessbar,  load_textarea]),
        ]
    )
    return [loadcard, dropdowncard]


def get_clustertab():
    clustermap = dbc.Card(dcc.Graph(id="clustermap"), body=True)
    return dbc.Tab(
        dbc.Card(
            [
                dbc.CardHeader("Show common routes for common start/end points"),
                dbc.CardBody(clustermap),
            ]
        ),
        label="Common routes ▶",
        tab_id="clustertab",
    )


def get_violintab():
    violinfactor_dropdown = dbc.Card(
        [
            dbc.CardHeader("Select a factor to analyze"),
            dbc.CardBody(
                dcc.Dropdown(
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
            ),
        ]
    )
    violinfactor_selected_file_txt = dbc.Card(
        [
            dbc.CardHeader("Click on point for details"),
            dbc.CardBody(
                dcc.Textarea(
                    id="violinfactor_selected_file_txt",
                    value="Click on a data point to show filename",
                    readOnly=True,
                    rows=13,
                    style={"width": "100%", "resize": "none", "padding": "5px"},
                )
            ),
        ]
    )
    dataandcontrols = [violinfactor_dropdown, violinfactor_selected_file_txt]
    violinplot = dcc.Graph(id="violinplot")
    plotcard = (
        dbc.Card(
            [
                dbc.CardHeader("Plot for different factors"),
                dbc.CardBody([violinplot]),
            ]
        ),
    )
    return dbc.Tab(
        dbc.Row([dbc.Col(dataandcontrols, width=5), dbc.Col(plotcard, width=7)]),
        label="Analyze categories",
        tab_id="violintab",
    )


def serve_layout():
    sessionid = str(uuid.uuid4())
    print(f"serve_layout: start with sessionid = {sessionid}")
    tabs = dbc.Tabs([get_clustertab(), get_violintab()], active_tab="clustertab")

    mainwindow = dbc.Row([dbc.Col(get_loadstuff(), width=4), dbc.Col(tabs, width=8)])

    return dbc.Container(
        [
            get_header(),
            mainwindow,
            dcc.Interval(id="progressinterval", disabled=True, interval=1000),
            dcc.Store(data=False, id="storedflag"),
            dcc.Store(data=sessionid, id="sessionid"),
            dcc.Store(data=0, id="numberoffiles"),
        ],
        fluid=True,
        className="dbc",
    )
