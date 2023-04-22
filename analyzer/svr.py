import logging

from dash import (
    Input,
    ALL,
    Output,
    State,
    callback,
    html,
    dcc,
    no_update,
)
import dash_bootstrap_components as dbc
import pandas as pd
from sklearn import svm
from utils.utilities import safe_int_float_kwargs

from dash_app.app_data_functions import get_data_from_pickle_session
from gpxfun.prepare_data import get_prepared_data

from .baseanalyzer import BaseAnalyzer


log = logging.getLogger("gpxfun." + __name__)

class AnalyzeSVR(BaseAnalyzer):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.Model = svm.SVR

    @staticmethod
    def dash_inputs_args(id):
        kerneldict = {"rbf": "RBF", "linear": "Linear", "poly": "Polynomial"}
        dashin=[]
        dashin += [dcc.Dropdown(options=kerneldict, value="rbf", id=id | {"id": "kernel"})]
        dashin += [dbc.Input(value="scale", type="text", id=id | {"id": "gamma"})]
        dashin += [dbc.Input(value="0.1", type="text", id=id | {"id": "epsilon"})]
        return dashin

    def dash_output(self):
        plot_predicted_vs_true = self.plot_predicted_vs_true()
        tabs = dbc.Tabs(
            [
                dbc.Tab(
                    html.Div(
                        [
                            html.Div(f"{len(self.d)} data points used (outliers excluded)"),
                            html.Div("Cross-validation scores: " + " ".join(["{0:3.2f}".format(x) for x in self.cvscores])),
                        ]
                    ),
                    label="Result infos",tab_id="coeffs"
                ),
                dbc.Tab([plot_predicted_vs_true], label="Prediction vs. true value",tab_id="plot")
            ]
            ,active_tab="plot"
        )
        return tabs

@callback(
    Output({"component": "analyzerresult", "analyzerid": "AnalyzeSVR"}, "children"),
    Input({"component": "analyzerinputs", "analyzerid": "AnalyzeSVR", "id":ALL}, "value"),
    Input({"component": "analyzerinputs", "analyzerid": "AnalyzeSVR", "id":ALL}, "id"),
    Input("storedflag", "data"),
    State("sessionid", "data"),
    Input("cluster_dropdown", "value"),
    Input("target_variable_dropdown", "value"),
    prevent_initial_call=True,
)
def callback_svr(values, ids, storedflag, sessionid, cluster, y_variable):
    if not storedflag or len(ids) == 0 or len(cluster) == 0:
        return no_update
    log.debug(f"callback svr: values = {values} ids = {ids} cluster = {cluster} ")
    ids = [x.get("id") for x in ids]
    kwargs = dict(zip(ids, values))
    # some options have default values as strings but are otherwise expected to be numeric
    kwargs = safe_int_float_kwargs(kwargs)
    log.debug(f"callback svr kwargs = {kwargs}")
    if None in kwargs.values():
        log.error("callback svr called with missing arguments")
        return no_update
    dr, _ = get_data_from_pickle_session(sessionid)
    dr = get_prepared_data(dr, cluster=cluster)
    a = AnalyzeSVR(dr)
    a.analyze(y_variable=y_variable, **kwargs)
    return a.dash_output()
