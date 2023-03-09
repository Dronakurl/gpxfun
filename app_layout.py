""" 
Layout for the dash app, to be used in the main app.py
"""
# ea39b8
import uuid
import logging
from utilities import getdirlist

from dash import dcc, html, dash_table
from plots import blank_fig
import dash_bootstrap_components as dbc

log = logging.getLogger("gpxfun." + __name__)
# MYCOLOR = "#ea39b8"
MYCOLOR = "white"


def getsessionids():
    opts = {}
    for sessionpath in getdirlist("sessions", withpath=True):
        opts[sessionpath.name] = sessionpath.name
    return opts


def get_header():
    return html.H4(
        [
            html.B("🚲 Bike route analyzer 🚲", style={"color": MYCOLOR}),
            html.Span(" - What's the fastest way from A to B? "),
        ],
        style={"margin-top": "5px", "text-align": "center"},
        className="bg-primary text-white p-2 mb-2 text-center",
    )


def get_loadstuff():
    uploadfield = dcc.Upload(
        id="upload-data",
        children=dbc.Button("Upload gpx files"),
        multiple=True,
    )
    progessbar = dbc.Progress(
        value=0,
        id="progressbar",
        label="no files to load",
        color=MYCOLOR,
        style={"color": "black", "margin-bottom": "10px", "margin-top": "10px"},
    )
    load_textarea = dcc.Textarea(
        id="load_textarea",
        value="",
        readOnly=True,
        rows=5,
        style={
            "width": "100%",
            "resize": "none",
            "padding": "5px",
            "margin-top": "5px",
            "font-size": "9pt",
            "font-family": "Ubuntu Mono, mono",
        },
    )
    startend_cluster_dropdown = dcc.Dropdown(
        options={
            "readdatafirst": "Load data first",
        },
        placeholder="select start/end combinations",
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
        placeholder="select routes",
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
            dbc.CardBody(
                [
                    startend_cluster_dropdown,
                    cluster_dropdown,
                ]
            ),
        ]
    )
    loadcard = dbc.Card(
        [
            dbc.CardHeader("Load GPX data"),
            dbc.CardBody([uploadfield, progessbar, picksessionid, load_textarea]),
            # dbc.CardBody([uploadfield, progessbar,  load_textarea]),
        ],
        style={"margin-bottom": "5px"},
    )
    return [loadcard, dropdowncard]


def get_clustertab():
    clustermap = dbc.Card(dcc.Graph(id="clustermap", figure=blank_fig()), body=True)
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
                        "startendcluster": "Start/End Cluster",
                        "cluster": "Cluster",
                        "wochentag": "Weekday",
                        "jahreszeit": "Season",
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
                    style={
                        "width": "100%",
                        "resize": "none",
                        "padding": "5px",
                        "font-size": "9pt",
                        "font-family": "Ubuntu Mono, mono",
                    },
                )
            ),
        ]
    )
    dataandcontrols = [violinfactor_dropdown, violinfactor_selected_file_txt]
    violinplot = dcc.Graph(id="violinplot", figure=blank_fig())
    plotcard = (
        dbc.Card(
            [
                dbc.CardHeader("Plot for different factors"),
                dbc.CardBody([violinplot]),
            ]
        ),
    )
    return dbc.Tab(
        dbc.Row([dbc.Col(dataandcontrols, width=3), dbc.Col(plotcard, width=9)]),
        label="Analyze categories ▶",
        tab_id="violintab",
    )


def get_tabletab():
    table = dash_table.DataTable(id="statisticstable")
    fig = dcc.Graph(id="statisticstimeseries", figure=blank_fig())
    newtable = html.Div(id="statisticsnewtable")

    return dbc.Tab(
        dbc.Card(
            [
                dbc.CardHeader("Show basic pivot with clusters (cluster filter do not apply)"),
                dbc.CardBody([fig, table, newtable]),
            ]
        ),
        label="Pivot ▶",
        tab_id="statistics_tab",
    )


def get_analyzertab():
    analyzer_dropdown = dcc.Dropdown(
        options={
            "readdatafirst": "Load data first",
        },
        placeholder="select analyzer",
        id="analyzer_dropdown",
        style={
            "width": "100%",
            "margin-bottom": "5px",
        },
    )
    analyzeroptions = dbc.Card("", body=True, id="analyzeroptionscard")
    analyzerresults = dbc.Card(
        [
            dbc.CardHeader("Results from chosen analyzer"),
            dbc.CardBody("", id="analyzerresultscard"),
        ],
    )
    return dbc.Tab(
        dbc.Card(
            [
                dbc.CardHeader("Analyze routes using statistical models"),
                dbc.CardBody(
                    dbc.Row(
                        [
                            dbc.Col([analyzer_dropdown, analyzeroptions], width=4),
                            dbc.Col(analyzerresults, width=8),
                        ]
                    )
                ),
            ]
        ),
        label="Models",
        tab_id="analyzer_tab",
    )


def serve_layout():
    sessionid = str(uuid.uuid4())
    log.debug(f"serve_layout: start with sessionid = {sessionid}")
    tabs = dbc.Tabs(
        [
            get_tabletab(),
            get_clustertab(),
            get_violintab(),
            get_analyzertab(),
        ],
        active_tab="statistics_tab",
        style={"margin-bottom": "5px"},
    )

    mainwindow = dbc.Row([dbc.Col(get_loadstuff(), width=3), dbc.Col(tabs, width=9)])

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
