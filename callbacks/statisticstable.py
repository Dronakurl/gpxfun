import logging

from dash import Input, Output, State, callback, ctx, no_update, dash_table
from dash_bootstrap_templates import load_figure_template

# import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from app_data_functions import get_data_from_pickle_session
from plots import TEMPLATE

log = logging.getLogger("gpxfun." + __name__)


@callback(
    Output("statisticsnewtable", "children"),
    Output("statisticstimeseries", "figure"),
    Input("storedflag", "data"),
    State("sessionid", "data"),
    prevent_initial_call=True,
)
def statisticstable(storedflag, sessionid):
    """table with statistics"""
    log.debug(str(ctx.triggered_id))
    if storedflag == False:
        return [no_update]*2
    dr, _ = get_data_from_pickle_session(sessionid)
    if len(dr) < 1:
        return [no_update]*2
    #     from geopy.geocoders import Nominatim
    # >>> geolocator = Nominatim(user_agent="specify_your_app_name_here")
    # >>> location = geolocator.reverse("52.509669, 13.376294")
    # >>> print(location.address)
    # Potsdamer Platz, Mitte, Berlin, 10117, Deutschland, European Union
    # get plot
    dx = dr[["filename", "startdatetime", "startendcluster", "cluster"]].copy()
    cats = list(dx.startendcluster.cat.categories)
    log.debug(f"categories of startendcluster: {cats}")
    # dx["startendcluster"] = dx.startendcluster.cat.add_categories("other")
    # dx["startendcluster"] = dx.startendcluster.fillna("other")
    # dx["cluster"] = dx.cluster.cat.add_categories("other")
    # dx["cluster"] = dx.cluster.fillna("other")
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
    dx.cluster = dx.cluster.str.extract("\d+_(.+)")
    dp = pd.pivot_table(
        dx,
        "filename",
        index=["cluster"],
        columns=["startendcluster"],
        aggfunc=["count"],
        margins=True,
        observed=True,
        dropna=False,
    ).reset_index()
    dp.columns = dp.columns.droplevel()
    dp = dp.rename({"": "Cluster"}, axis=1)
    namemapper = lambda x: x if not str(x).isdigit() else "Startendcluster " + str(x)
    cols = [{"name": namemapper(i), "id": str(i)} for i in dp.columns]
    datatable = dash_table.DataTable(
        columns=cols,
        data=dp.to_dict("records"),
        # filter_action="native",
        style_header={"font-weight": "bold", "background-color": "var(--bs-card-cap-bg)"},
        style_cell=dict(width="14%"),
        style_cell_conditional=[{"if":{"column_id":"All"},"background-color": "var(--bs-card-cap-bg)"}],
        style_data_conditional=[{"if":{"row_index":len(dp)-1},"background-color": "var(--bs-card-cap-bg)"}],

        # style_table=dict(width="60%")
        # style_filter={"display":"none","height":"0px"}
    )
    # dp.columns = pd.MultiIndex.from_tuples(
    #     [("Startend cluster", x[1]) for x in list(dp.columns)]
    # )
    # dp.index.name = "Cluster"
    # newtable = dbc.Table.from_dataframe(
    #     dp,
    #     striped=False,
    #     bordered=True,
    #     hover=False,
    #     index=True,
    #     style={
    #         "font-size": "8pt",
    #         "font-family": "Roboto Mono, mono",
    #         "padding": "0px",
    #         "background-color": "var(--bs-body-bg)"
    #     },
    # )
    return datatable, fig
