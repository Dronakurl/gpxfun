import logging

from dash import Input, Output, State, callback, ctx, html, no_update
import numpy as np

from app_data_functions import get_data_from_pickle_session
from plots import plotaroute
from prepare_data import y_variables_dict


log = logging.getLogger("gpxfun." + __name__)


@callback(
    Output("clustermap", "figure"),
    Output("analyzernodatapoints", "children"),
    Input("storedflag", "data"),
    Input("cluster_dropdown", "value"),
    State("sessionid", "data"),
    Input("target_variable_dropdown", "value"),
    prevent_initial_call=True,
)
def showmap(storedflag, clusters, sessionid, y_variable):
    """Draws a map with the most common routes"""
    log.debug(str(ctx.triggered_id) + " " + str(clusters))
    if storedflag == False or clusters is None:
        return [no_update] * 2
    dr, most_imp_clusters = get_data_from_pickle_session(sessionid)
    dr = dr[dr.cluster.isin(clusters)]
    if len(dr) < 1:
        return [no_update] * 2
    mics = most_imp_clusters
    mics = mics[mics.cluster.isin(clusters)]
    mics = mics.drop(["cluster", "filename"], axis=1)
    mics = mics.drop_duplicates()
    points = {}
    points["start"] = list(zip(mics.start_lat, mics.start_lon))
    points["end"] = list(zip(mics.ende_lat, mics.ende_lon))
    fig = plotaroute(dr, groupfield="cluster", zoom=-1, title=None, specialpoints=points)
    return fig, analyzerstats(dr, y_variable)


def analyzerstats(dr, y_variable):
    """The small statistics field in the analyzer tab"""
    return html.Div(
        [
            html.B("Data points: "),
            html.Span(str(len(dr))),
            html.Br(),
            html.B("Outliers: "),
            html.Span(str(len(dr[dr.is_outlier]))),
            html.Br(),
            html.B(f"Mean {y_variables_dict.get(y_variable,'ERROR')}: "),
            html.Span(f"{np.mean(dr[y_variable]):.2f}"),
        ],
        style={"font-size": "10pt", "font-family": "Roboto mono, mono"},
    )
