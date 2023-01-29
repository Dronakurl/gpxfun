"""
Plot functions
"""
import calendar
from typing import Optional

from dash_bootstrap_templates import load_figure_template
import pandas as pd
import plotly.express as px
import plotly.express as px


def prepareplotdata(
    route,
    groupfield: Optional[str] = None,
    routevar: str = "route_inter",
):
    """Plot one or more routes"""
    if groupfield is not None:
        assert type(route) == pd.DataFrame
        outputdf = (
            route.groupby(["dateiname"], group_keys=True)
            .apply(lambda r: pd.DataFrame(r.iloc[0][routevar], columns=["lon", "lat"]))
            .reset_index(drop=False)
            .drop("level_1", axis=1)
        )
        outputdf = outputdf.merge(
            route.loc[:, list(set(["dateiname", groupfield]))],
            on="dateiname",
        )
    else:
        assert type(route) == list
        outputdf = pd.DataFrame(route, columns=["lon", "lat"])
    return outputdf


def plotaroute(
    route,
    zoom: int = 13,
    groupfield: Optional[str] = None,
    plottype: str = "map",
    routevar: str = "route_inter",
    title: Optional[str] = "",
    specialpoints: Optional[list] = None
):
    """
    plot a given route from a given route
    """
    y = prepareplotdata(route, groupfield, routevar=routevar)
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
            template="slate",
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 20, "l": 0, "b": 0})
    elif plottype == "line":
        fig = px.line(y, y="lat", color=groupfield)
    else:
        fig = None
    return fig
# with open("pickles/df.bk3.pickle","rb") as f:
#     d=pickle.load(f)
# plotaroute(d,groupfield="cluster")

def violin(dr: pd.DataFrame, 
           cat_variable: str = "wochentag"):
    load_figure_template("slate")
    if cat_variable=="cluster":
        cat_order={"cluster": list(dr.cluster.drop_duplicates().sort_values())}
    elif cat_variable=="wochentag":  
        cat_order={"wochentag": list(calendar.day_name[0:5])}
    elif cat_variable=="jahreszeit":
        cat_order={"jahreszeit": ["spring","summer","autumn","winter"]}
    else:
        cat_order={cat_variable: list(dr[cat_variable].drop_duplicates().sort_values())}
    fig = px.violin(
        dr,
        y="dauer",
        x=cat_variable,
        # color="wochentag",
        box=True,
        points="all",
        hover_data=["cluster","dateiname"],
        category_orders=cat_order,
        labels={"jahreszeit": "Jahreszeit", "y": "Dauer"},
        template="slate",
    )
    fig.update_layout(
        bargap=0.2,
        xaxis_title="Cluster",
        font=dict(family="Ubuntu, sans",size=14),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    return fig
# violin(dr,"wochentag")
# violin(dr,"jahreszeit")
# violin(dr,"cluster")

