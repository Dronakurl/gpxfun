import pandas as pd
import plotly.express as px


def plotaroute(route, zoom: int = 12, groupfield: str = None, plottype: str = "map", routevar: str="route_inter"):
    """Plot one or more routes"""
    if groupfield is not None:
        assert type(route) == pd.DataFrame
        y = (
            route.groupby(["dateiname"],group_keys=True)
            .apply(lambda r: pd.DataFrame(r.iloc[0][routevar], columns=["lon", "lat"]))
            .reset_index(drop=False)
            .drop("level_1", axis=1)
        )
        y = (
            y.merge(
                route.loc[:, list(set(["dateiname", groupfield]))],
                on="dateiname",
            )
        )
    else:
        assert type(route) == list
        y = pd.DataFrame(route, columns=["lon", "lat"])
    if plottype == "map":
        fig = px.scatter_mapbox(
            y,
            lat="lat",
            lon="lon",
            # color_discrete_sequence=["fuchsia"],
            zoom=zoom,
            color=groupfield,
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.show()
    elif plottype == "line":
        fig = px.line(y, y="lat", color=groupfield)
        fig.show()
