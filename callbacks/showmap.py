import logging

from dash import Input, Output, State, callback, ctx, no_update

from app_data_functions import get_data_from_pickle_session
from plots import plotaroute


log = logging.getLogger("gpxfun." + __name__)


@callback(
    Output("clustermap", "figure"),
    Input("storedflag", "data"),
    Input("cluster_dropdown", "value"),
    State("sessionid", "data"),
    prevent_initial_call=True,
)
def showmap(storedflag, clusters, sessionid):
    """Draws a map with the most common routes"""
    log.debug(str(ctx.triggered_id) + " " + str(clusters))
    if storedflag == False or clusters is None:
        return no_update
    dr, most_imp_clusters = get_data_from_pickle_session(sessionid)
    dr = dr[dr.cluster.isin(clusters)]
    if len(dr) < 1:
        return no_update
    mics = most_imp_clusters
    mics = mics[mics.cluster.isin(clusters)]
    mics = mics.drop(["cluster", "dateiname"], axis=1)
    mics = mics.drop_duplicates()
    points = {}
    points["start"] = list(zip(mics.start_lat, mics.start_lon))
    points["end"] = list(zip(mics.ende_lat, mics.ende_lon))
    fig = plotaroute(
        dr, groupfield="cluster", zoom=-1, title=None, specialpoints=points
    )
    return fig
