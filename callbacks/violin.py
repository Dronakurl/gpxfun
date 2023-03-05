import json
import logging

from dash import Input, Output, State, callback, ctx, no_update

from app_data_functions import get_data_from_pickle_session
from plots import violin


log = logging.getLogger("gpxfun.callbacks." + __name__)


@callback(
    Output("violinplot", "figure"),
    Input("violinfactor", "value"),
    Input("storedflag", "data"),
    Input("cluster_dropdown", "value"),
    State("sessionid", "data"),
    prevent_initial_call=True,
)
def showhists(violinfactor, storedflag, clusters, sessionid):
    """Show plots to analyze the times"""
    log.debug(str(ctx.triggered_id))
    if storedflag == False or clusters is None:
        return no_update
    dr, _ = get_data_from_pickle_session(sessionid)
    dr = dr[dr.cluster.isin(clusters)]
    fig = violin(dr, violinfactor)
    return fig


@callback(
    Output("violinfactor_selected_file_txt", "value"),
    Input("violinplot", "clickData"),
    Input("cluster_dropdown", "value"),
    State("storedflag", "data"),
    State("sessionid", "data"),
    prevent_initial_call=True,
)
def clickondata(clickdata, clusters, storedflag, sessionid):
    """Show information on the clicked data point"""
    log.debug("CALLBACK clickondata: " + str(ctx.triggered_id))
    if storedflag == False or clusters is None:
        return no_update
    dr, _ = get_data_from_pickle_session(sessionid)
    if clickdata is not None:
        # I don't know, why I need this, but the given clickdata is not a proper dict at first
        clickeddict = json.loads(json.dumps(clickdata))
        # import pdb; pdb.set_trace()
        clicked_file = clickeddict["points"][0]["customdata"][0]
        clickedseries = dr[dr["dateiname"] == clicked_file].iloc[0]
        clickedseries = clickedseries.drop(["route_inter"])
        return "\n".join(f"{clickedseries}".split("\n")[0:-1])
    else:
        return "Click on a data point to show filename and infos"
