import logging

from dash import Dash, Input, MATCH, Output, State, callback, ctx, dcc, html, no_update
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from app_data_functions import get_data_from_pickle_session, parse_and_cluster
from plots import TEMPLATE, plotaroute, violin

log = logging.getLogger("gpxfun." + __name__)

@callback(
    Output("statisticsnewtable", "children"),
    Output("statisticstimeseries", "figure"),
    Input("storedflag", "data"),
    Input("cluster_dropdown", "value"),
    State("sessionid", "data"),
    prevent_initial_call=True,
)
def statisticstable(storedflag, clusters, sessionid):
    """table with statistics"""
    log.debug("CALLBACK statisticstable: " + str(ctx.triggered_id))
    if storedflag == False or clusters is None:
        return no_update, no_update
    dr, _ = get_data_from_pickle_session(sessionid)
    if len(dr) < 1:
        return no_update, no_update
    #     from geopy.geocoders import Nominatim
    # >>> geolocator = Nominatim(user_agent="specify_your_app_name_here")
    # >>> location = geolocator.reverse("52.509669, 13.376294")
    # >>> print(location.address)
    # Potsdamer Platz, Mitte, Berlin, 10117, Deutschland, European Union
    # get plot
    dx = dr[["dateiname", "startdatetime", "startendcluster", "cluster"]].copy()
    cats = list(dx.startendcluster.cat.categories)
    dx["startendcluster"] = dx.startendcluster.cat.add_categories("other")
    dx["startendcluster"] = dx.startendcluster.fillna("other")
    dx["cluster"] = dx.cluster.cat.add_categories("other")
    dx["cluster"] = dx.cluster.fillna("other")
    load_figure_template(TEMPLATE)
    fig = px.histogram(
        dx,
        height=200,
        x="startdatetime",
        color="startendcluster",
        category_orders={"startendcluster": [*cats, "other"]},
        template=TEMPLATE,
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    # Get statisticstable
    dp = pd.pivot_table(
        dx,
        "dateiname",
        index=["cluster"],
        columns=["startendcluster"],
        aggfunc=["count"],
        margins=True,
        observed=True,
        dropna=False,
    )
    dp = dp.sort_index()
    # dp.columns = dp.columns.droplevel()
    dp.columns = pd.MultiIndex.from_tuples(
        [("Startend cluster", x[1]) for x in list(dp.columns)]
    )
    dp.index.name = "Cluster"
    newtable = dbc.Table.from_dataframe(
        dp,
        striped=True,
        bordered=True,
        hover=True,
        index=True,
        style={
            "font-size": "8pt",
            "font-family": "Roboto Mono, mono",
            "padding": "0px",
        },
    )
    return newtable, fig
