from dash import dcc, html, Dash, Output, Input, State, ctx, MATCH, ALL, dash_table
import dash_bootstrap_components as dbc
import dash
import io
import base64

# setup dash app
latofont = ['https://fonts.googleapis.com/css2?family=Lato&display=swap']
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.css"
dashapp = Dash(__name__, external_stylesheets=[dbc.themes.SLATE, dbc_css, latofont])
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
    width=4
)

convplot = dbc.Col(
    [
        dbc.Card(
            [
                dbc.CardHeader("map"),
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


@dashapp.callback(Output("plot","children"),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def showplot(contents,filenames):
    if contents is not None:    
        tabs=[]
        for ii in range(len(contents)):
            cc=contents[ii]
            filename=filenames[ii]
            content_type, content_string = cc.split(',')
            decoded = base64.b64decode(content_string)
            f=io.StringIO(decoded.decode('utf-8'))
            vf=voltagefile.VoltageFile(infile=f)
            outtext=vf.transformrigol()
            fig=vf.plotvtot()
            fig.update_layout( margin=dict(l=20, r=20, t=40, b=20))
            tabs.append( 
                dbc.Tab(
                    [
                        dcc.Graph(figure=fig,style={"height":"300px"}),
                        dcc.Textarea(
                            value=outtext,
                            id={'type':'textoutput','index':filename},
                            style={"display":"none"}
                        ),
                        dbc.Button("save file",id={'type': 'savebutton', 'index':filename},color="primary")
                    ],
                    label=filename
                )
            )
            amp=   str(vf.wpars["amplitude"])+" V"
            omega= str(vf.wpars["frequency"])+" Hz"
            offset=str(vf.wpars["offset"])+" V"
        children=dbc.Tabs(tabs)
    else:
        children=[dbc.Alert("nothing to plot yet",color="primary")]
        amp="no osci data yet"
        omega="no osci data yet"
        offset="no osci data yet"
    return children,amp,omega,offset

app=dashapp.server
app.secret_key = 'super secret key'

if __name__ == '__main__':
    dashapp.run_server(debug=True)

# start with: gunicorn app:app -b :8000
