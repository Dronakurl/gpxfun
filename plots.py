"""
Plot functions
"""
import calendar
from typing import Optional

from dash_bootstrap_templates import load_figure_template
import numpy as np
import planar
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def get_plotting_zoom_level(longitudes=None, latitudes=None, lonlat_pairs=None):
    """Function documentation:\n
    Basic framework adopted from Krichardson under the following thread:
    https://community.plotly.com/t/dynamic-zoom-for-mapbox/32658/7
    # NOTE:
    # THIS IS A TEMPORARY SOLUTION UNTIL THE DASH TEAM IMPLEMENTS DYNAMIC ZOOM
    # in their plotly-functions associated with mapbox, such as go.Densitymapbox() etc.
    Returns the appropriate zoom-level for these plotly-mapbox-graphics along with
    the center coordinate tuple of all provided coordinate tuples.
    """
    # Check whether the list hasn't already be prepared outside this function
    if lonlat_pairs is None:
        # Check whether both latitudes and longitudes have been passed,
        # or if the list lenghts don't match
        if (latitudes is None or longitudes is None) or (
            len(latitudes) != len(longitudes)
        ):
            # Otherwise, return the default values of 0 zoom and the coordinate origin as center point
            return 0, (0, 0)
        # Instantiate collator list for all coordinate-tuples
        lonlat_pairs = [(longitudes[i], latitudes[i]) for i in range(len(longitudes))]
    # Get the boundary-box via the planar-module
    b_box = planar.BoundingBox(lonlat_pairs)
    # In case the resulting b_box is empty, return the default 0-values as well
    if b_box.is_empty:
        return 0, (0, 0)
    # Otherwise, get the area of the bounding box in order to calculate a zoom-level
    area = b_box.height * b_box.width
    # * 1D-linear interpolation with numpy:
    # - Pass the area as the only x-value and not as a list, in order to return a scalar as well
    # - The x-points "xp" should be in parts in comparable order of magnitude of the given area
    # - The zpom-levels are adapted to the areas, i.e. start with the smallest area possible of 0
    # which leads to the highest possible zoom value 20, and so forth decreasing with increasing areas
    # as these variables are antiproportional
    zoom = np.interp(
        x=area,
        xp=[0, 5**-10, 4**-10, 3**-10, 2**-10, 1**-10, 1**-5],
        fp=[20, 17, 16, 15, 14, 7, 5],
    )
    # Finally, return the zoom level and the associated boundary-box center coordinates
    calccenter=b_box.center
    return int(zoom), {"lat": calccenter.y, "lon": calccenter.x}

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
                the groupfield column is included and also the dateiname column
    """
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
    load_figure_template("slate")
    if zoom==-1:
        (
            calczoom,
            calccenter,
        ) = get_plotting_zoom_level(longitudes=y.lon, latitudes=y.lat)
    else:
        calczoom=zoom
        calccenter=None
    y[groupfield] = y[groupfield].astype("str")
    mycols=[["#8A1A00", "#008A1A", "#1A008A", "#8A5E00", "#008A5E", "#5E008A",],
            [ "#992D14", "#14992D", "#2D1499", "#997014", "#149970", "#701499",]]
    fig = px.scatter_mapbox(
        y,
        lat="lat",
        lon="lon",
        color_discrete_sequence=mycols[1],
        zoom=calczoom - 2,
        center=calccenter,
        color=groupfield,
        title=title,
        template="slate",
    )
    if specialpoints != None and len(specialpoints.keys())>0:
        coln=0
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
            coln+=1
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 20, "l": 0, "b": 0})
    return fig


def violin(dr: pd.DataFrame, cat_variable: str = "wochentag"):
    load_figure_template("slate")
    if cat_variable == "cluster":
        cat_order = {"cluster": list(dr.cluster.drop_duplicates().sort_values())}
    elif cat_variable == "wochentag":
        cat_order = {"wochentag": list(calendar.day_name[0:5])}
    elif cat_variable == "jahreszeit":
        cat_order = {"jahreszeit": ["spring", "summer", "autumn", "winter"]}
    else:
        cat_order = {
            cat_variable: list(dr[cat_variable].drop_duplicates().sort_values())
        }
    fig = px.violin(
        dr,
        y="dauer",
        x=cat_variable,
        # color="wochentag",
        box=True,
        points="all",
        hover_data=["cluster", "dateiname"],
        category_orders=cat_order,
        labels={"jahreszeit": "Jahreszeit", "y": "Dauer"},
        template="slate",
    )
    fig.update_layout(
        bargap=0.2,
        xaxis_title=cat_variable.capitalize(),
        yaxis_title="Duration",
        font=dict(family="Ubuntu, sans", size=14),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )
    return fig


# violin(dr,"wochentag")
# violin(dr,"jahreszeit")
# violin(dr,"cluster")
