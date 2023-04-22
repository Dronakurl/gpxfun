"""
Plot functions
"""
import calendar
import logging
from typing import Optional

from dash_bootstrap_templates import load_figure_template
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from gpxfun.prepare_data import y_variables_dict

log = logging.getLogger("gpxfun." + __name__)

# TEMPLATE = "vapor"
TEMPLATE = "sketchy"
# TEMPLATE = "darkly"


def prepareplotdata(
    route,
    groupfield: Optional[str] = None,
    routevar: str = "route_inter",
):
    """
    prepare data for plotaroute function and convert the routevar column
    :param route: pandas DataFrame containing a field routevar wher a list of
                    points with longitudes and latitudes tuples is stored
    :type router: pandas.DataFrame
    :param groupfield: column name containing a variable to group the data by
    :type groupfield: str
    :param routevar: column name containing in route DataFrame containing the routes
    :type routevar: str
    :returns: a pandas DataFrame with columns lon and lat, containing the
                longitudes and latitudes of the routes to plot
                to be used by plotaroute function
                the groupfield column is included and also the filename column
    """
    if groupfield is not None:
        assert type(route) == pd.DataFrame
        outputdf = (
            route.groupby(["filename"], group_keys=True)
            .apply(lambda r: pd.DataFrame(r.iloc[0][routevar], columns=["lon", "lat"]))
            .reset_index(drop=False)
            .drop("level_1", axis=1)
        )
        outputdf = outputdf.merge(
            route.loc[:, list(set(["filename", groupfield]))],
            on="filename",
        )
    else:
        assert type(route) == list
        outputdf = pd.DataFrame(route, columns=["lon", "lat"])
    return outputdf


def plotaroute(
    route: pd.DataFrame,
    zoom: int = -1,
    groupfield: Optional[str] = None,
    routevar: str = "route_inter",
    title: Optional[str] = "",
    specialpoints: Optional[dict] = None,
):
    """
    plot a given route from a given route
    :param route: a pandas dataset with route data. each row contains a whole route.
            the pandas DataFrame is passed to the prepareplotdata first
    :type route: pd.DataFrame
    :param zoom: zoom level to be used by the mapbox function in plotly,
                default is -1 where the dynamic-zoom-for-mapbox function is applied
                to get the right zoom level automatically
    :type zoom: int
    :param groupfield: column name containing a variable to group the data by
    :type groupfield: str
    :param routevar: column name containing in route DataFrame containing the routes
    :type routevar: str
    :param title: Title of the plot
    :type title: str
    :param specialpoints: a dictionary containing special points to be plotted
            as markers on the map
            the dictionary labels are used to label the point
    :type specialpoints: dict
    """
    y = prepareplotdata(route, groupfield, routevar=routevar)
    load_figure_template(TEMPLATE)
    if zoom == -1:
        calczoom = 12
        calccenter = None
    else:
        calczoom = zoom
        calccenter = None
    y[groupfield] = y[groupfield].astype("str")
    mycols = [
        [
            "#8A1A00",
            "#008A1A",
            "#1A008A",
            "#8A5E00",
            "#008A5E",
            "#5E008A",
        ],
        [
            "#992D14",
            "#14992D",
            "#2D1499",
            "#997014",
            "#149970",
            "#701499",
        ],
    ]
    fig = px.scatter_mapbox(
        y,
        lat="lat",
        lon="lon",
        color_discrete_sequence=mycols[1],
        zoom=calczoom,
        center=calccenter,
        color=groupfield,
        title=title,
        template=TEMPLATE,
    )
    if specialpoints != None and len(specialpoints.keys()) > 0:
        coln = 0
        for label, points in specialpoints.items():
            # mycols = px.colors.qualitative.Set1.copy()
            fig.add_trace(
                go.Scattermapbox(
                    lat=list(list(zip(*points))[0]),
                    lon=list(list(zip(*points))[1]),
                    mode="markers",
                    marker=go.scattermapbox.Marker(size=14, color=mycols[1][coln]),
                    name=label,
                )
            )
            coln += 1
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 20, "l": 0, "b": 0})
    return fig


def violin(dr: pd.DataFrame, cat_variable: str = "weekday", y_variable: str = "duration"):
    """ plot a violin plot with the given variables """
    log.debug(f"violin plot with y_variable={y_variable}")
    load_figure_template(TEMPLATE)
    if cat_variable == "cluster":
        cat_order = {"cluster": list(dr.cluster.drop_duplicates().sort_values())}
    elif cat_variable == "weekday":
        cat_order = {"weekday": list(calendar.day_name[0:5])}
    elif cat_variable == "season":
        cat_order = {"season": ["spring", "summer", "autumn", "winter"]}
    else:
        cat_order = {cat_variable: list(dr[cat_variable].drop_duplicates().sort_values())}
    fig = px.strip(
        dr,
        y=y_variable,
        x=cat_variable,
        hover_data=["cluster", "filename"],
        category_orders=cat_order,
        stripmode="overlay",
        labels={"season": "Season", "y": y_variable, "is_outlier": "Outlier?"},
        color="is_outlier",
        template=TEMPLATE,
    )
    fig.add_trace(
        go.Violin(
            y=dr[dr.is_outlier == False][y_variable],
            x=dr[dr.is_outlier == False][cat_variable],
            box=go.violin.Box(visible=True),
            points=False,
            offsetgroup=3,
            name="Distribution",
        )
    )
    fig.update_layout(
        bargap=0.2,
        xaxis_title=cat_variable.capitalize(),
        yaxis_title=y_variables_dict.get(y_variable, "ERROR"),
        yaxis_title_standoff=30,
        font=dict(family="Ubuntu, sans", size=14),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )
    return fig


def blank_fig():
    load_figure_template(TEMPLATE)
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=TEMPLATE)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig


# if __name__ == "__main__":
#     dx = d[["startdatetime", "startendcluster", "cluster"]].copy()
#     dx["startendcluster"] = dx.startendcluster.cat.add_categories("other").fillna(
#         "other"
#     )
#     # dx["cluster"]=dx.cluster.cat.add_categories("other").fillna("other")
#     px.histogram(
#         dx,
#         x="startdatetime",
#         color="startendcluster",
#         category_orders={"startendcluster": [0, 1, "other"]},
#     )


