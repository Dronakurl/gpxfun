import logging
import pickle
from pathlib import Path
from utilities import save_int_list_cast

from dash import Input, Output, State, callback, ctx, no_update

log = logging.getLogger("gpxfun." + __name__)


@callback(
    Output("cluster_dropdown", "options"),
    Output("cluster_dropdown", "value"),
    Input("startend_cluster_dropdown", "value"),
    Input("storedflag", "data"),
    State("sessionid", "data"),
    prevent_initial_call=True,
)
def update_cluster_dropdown(startendclusters, storedflag, sessionid):
    """Initialize the dropdown for the route cluster using startendcluster"""
    log.debug(str(ctx.triggered_id))
    if storedflag == False:
        return [no_update] * 2
    with open(Path("sessions") / sessionid / "most_imp_clusters.pickle", "rb") as f:
        most_imp_clusters = pickle.load(f)
    clusters = most_imp_clusters[most_imp_clusters.startendcluster.isin(save_int_list_cast(startendclusters))].cluster
    cluster_dropdown_opts = {}
    for clu in list(clusters):
        cluster_dropdown_opts[clu] = "Route " + str(clu)
    # cluster_dropdown_opts["all"]="all routes"
    return cluster_dropdown_opts, clusters


@callback(
    Output("startend_cluster_dropdown", "options"),
    Output("startend_cluster_dropdown", "value"),
    Input("storedflag", "data"),
    State("sessionid", "data"),
    prevent_initial_call=True,
)
def update_startend_dropdown(storedflag, sessionid):
    """Initialize the dropdown for the startendcluster"""
    log.debug("CALLBACK update_startend_dropdown: " + str(ctx.triggered_id))
    if storedflag == False:
        return [no_update] * 2
    with open(Path("sessions") / sessionid / "most_imp_clusters.pickle", "rb") as f:
        most_imp_clusters = pickle.load(f)
    startendcluster_dropdown_opts = {}
    for cat in list(most_imp_clusters.startendcluster.cat.categories):
        startendcluster_dropdown_opts[cat] = "Start/end-combination " + str(cat)
    # cluster_dropdown_opts["all"]="All start/end-combinations"
    if len(startendcluster_dropdown_opts.keys())==0:
        log.error(f"No options could be derived from {most_imp_clusters}")
        return [no_update] * 2
    return startendcluster_dropdown_opts, [list(startendcluster_dropdown_opts.keys())[0]]
