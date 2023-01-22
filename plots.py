"""
Plot functions
"""
import pandas as pd
import plotly.express as px
from dash_bootstrap_templates import load_figure_template


def prepareplotdata(
    route,
    groupfield: str = None,
    routevar: str = "route_inter",
):
    """Plot one or more routes"""
    if groupfield is not None:
        assert type(route) == pd.DataFrame
        y = (
            route.groupby(["dateiname"], group_keys=True)
            .apply(lambda r: pd.DataFrame(r.iloc[0][routevar], columns=["lon", "lat"]))
            .reset_index(drop=False)
            .drop("level_1", axis=1)
        )
        y = y.merge(
            route.loc[:, list(set(["dateiname", groupfield]))],
            on="dateiname",
        )
    else:
        assert type(route) == list
        y = pd.DataFrame(route, columns=["lon", "lat"])

def plotaroute(
    route,
    zoom: int = 13,
    groupfield: str = None,
    plottype: str = "map",
    routevar: str = "route_inter",
    title: str = ""
):
    '''
    plot a given route from a given route
    '''
    y= prepareplotdata( route, groupfield, routevar= "route_inter")
    if plottype == "map":
        load_figure_template("slate")
        fig = px.scatter_mapbox(
            y,
            lat="lat",
            lon="lon",
            # color_discrete_sequence=["fuchsia"],
            zoom=zoom,
            color=groupfield,
            title=title,
            template="slate"
        )
        fig.update_layout(mapbox_style="open-street-map")
        # fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        # fig.update_layout( title_font_family="Ubuntu", title_font_color="red", )
    elif plottype == "line":
        fig = px.line(y, y="lat", color=groupfield)
    return fig

# # mittlere Zeit je Jahreszeit
# fig=px.histogram(d[d.arbeit],x="dauer",y="jahreszeit",orientation="h",histnorm="probability",
#     labels={"jahreszeit":"Jahreszeit","y":"Anteil"})
# fig.update_layout(
#     bargap=.2,
#     xaxis_title="Dauer",
#     # yaxis =p dict(
#         # tickmode = 'array',
#         # tickvals = [0,1,2,3,4,5,6],
#         # ticktext = ["Mo","Di","Mi","Do","Fr","Sa","So"]
#     # )
# )
# fig.show()

