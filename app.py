""" 
A dash app to visualize the results
"""
from dash import dcc, html, Dash, Output, Input, State, ctx, MATCH, ALL, dash_table
import dash_bootstrap_components as dbc
import dash
import pickle
import re
from plots import plotaroute, violin

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.css"
dashapp = Dash(__name__, external_stylesheets=[dbc.themes.SLATE, dbc_css])
dashapp.title = "GPX analyzer"

header = html.H4(
    "GPX analyzer - Was ist der schnellste Weg zur Arbeit? ",
    style={"margin-top":"5px"}
    # className="bg-primary text-white p-2 mb-2 text-center",
)

loadcard = dbc.Card(
    dcc.Upload(
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
    ),
    body=True,
)
loadstuff = dbc.Tab(loadcard, disabled=True, label="Load (tbd; use gpechse.py)")

showmaps = dbc.Tab(
    dbc.Card([dbc.CardHeader("Map of important clusters"), dbc.CardBody(id="mapplot")]),
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
    style={"width": "100%", "resize":"none","padding":"5px"},
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

tabs = dbc.Tabs([loadstuff, showmaps, violins], active_tab="violintab")

dashapp.layout = dbc.Container(
    [header, tabs, dcc.Store(id="store")],
    fluid=True,
    className="dbc",
)


# prepare all the data, read the dataset
with open("pickles/df.pickle", "rb") as f:
    d = pickle.load(f)
# get the names of the biggest clusters
imp_clusters = d.cluster.drop_duplicates()
imp_clusters = imp_clusters[imp_clusters.astype(bool)].sort_values()
imp_clusters = [x for x in imp_clusters if int(re.search("\D_(\d+)", x).group(1)) < 4]
dr = d[d.arbeit].copy()
# exclude some strange outliers
dr = dr[dr.dateiname != "20220920T075709000.gpx"]
dr.cluster = dr.cluster.apply(lambda x: x if x in imp_clusters else "sonstige")


@dashapp.callback(
    Output("mapplot", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def showmap(contents, filenames):
    """Update the map with clusters"""
    fig = plotaroute(
        dr,
        groupfield="cluster",
        title=None,
    )
    return [dcc.Graph(figure=fig)]


@dashapp.callback(
    Output("violinplot", "figure"),
    Input("violinfactor", "value"),
    State("upload-data", "contents"),
    State("upload-data", "filename"),
)
def showhists(violinfactor, contents, filenamesi):
    """Update the histogram or violin plots"""
    fig = violin(dr, violinfactor)
    return fig


@dashapp.callback(
    Output("violinfactor_selected_file_txt", "value"),
    Input("violinplot", "clickData"),
)
def clickondata(clickdata):
    """Show information on the clicked data point"""
    if clickdata is not None:
        # I don't know, why I need this
        import json
        clickeddict = json.loads(json.dumps(clickdata))
        clicked_file=clickeddict["points"][0]["customdata"][0]
        clickedseries=dr[dr["dateiname"]==clicked_file].iloc[0]
        clickedseries=clickedseries.drop(["route","route_inter"])
        return "\n".join(f"{clickedseries}".split("\n")[0:-1])
    else:
        return "Click on a data point to show filename and infos"


app = dashapp.server
app.secret_key = "super secret key"

if __name__ == "__main__":
    dashapp.run_server(debug=True)

# start with: gunicorn app:app -b :8000
