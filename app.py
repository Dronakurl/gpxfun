''' 
A dash app to visualize the results
'''
from dash import dcc, html, Dash, Output, Input, State, ctx, MATCH, ALL, dash_table
import dash_bootstrap_components as dbc
import dash
import pickle
import re
from plots import plotaroute

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.css"
dashapp = Dash(__name__, external_stylesheets=[dbc.themes.SLATE, dbc_css])
dashapp.title="GPX analyzer"

header = html.H4( "GPX analyzer", className="bg-primary text-white p-2 mb-2 text-center")

sidebar = dbc.Col(
    [
        dbc.Card(
            [
                html.H2("Upload files"),
                html.Hr(),
                dcc.Upload( 
                    id='upload-data', 
                    children=html.Div( [ 'Drag and Drop or ', html.A('Select Files') ]), 
                    multiple=True,
                    style={
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    }  
                ),
            ],
            body=True
        )
    ],
    width=3
)

convplot = dbc.Col(
    [
        dbc.Card(
            [
                dbc.CardHeader("map of important clusters"),
                dbc.CardBody(id="plot")
            ]
        )
    ],
    width=8
)

convtab=dbc.Row([sidebar,convplot])

tabs = dbc.Card(convtab)

dashapp.layout = dbc.Container(
    [
        header,
        tabs,
        dcc.Store(id="store"),
        dcc.Download(id="download"),
        dcc.Download(id="gendownload")
    ],
    fluid=True,
    className="dbc"
)


with open("pickles/df.pickle", "rb") as f:
    d = pickle.load(f)
# get the names of the biggest clusters
imp_clusters = d.cluster.drop_duplicates()
imp_clusters = imp_clusters[imp_clusters.astype(bool)].sort_values()
imp_clusters = [x for x in imp_clusters if int(re.search("\D_(\d+)", x).group(1)) < 4]

@dashapp.callback(Output("plot","children"),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def showplot(contents,filenames):
    fig=plotaroute(
        d[d.arbeit & d.cluster.isin(imp_clusters)],
        groupfield="cluster",
        title=None,
    )
    return [dcc.Graph(figure=fig)]

app=dashapp.server
app.secret_key = 'super secret key'

if __name__ == '__main__':
    dashapp.run_server(debug=True)

# start with: gunicorn app:app -b :8000
