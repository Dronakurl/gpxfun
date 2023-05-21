import logging

from dash import (
    ALL,
    Input,
    Output,
    State,
    callback,
    dash_table,
    dcc, # pyright: ignore
    html,
    no_update,
)
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px # pyright: ignore
from sklearn import linear_model

from dash_app.app_data_functions import get_data_from_pickle_session
from gpxfun.prepare_data import get_prepared_data

# from sklearn.model_selection import cross_val_score, train_test_split#, cross_val_predict, GridSearchCV
from gpxfun.prepare_data import y_variables_dict # pyright: ignore

from .baseanalyzer import BaseAnalyzer


log = logging.getLogger("gpxfun." + __name__)


class AnalyzeLinear(BaseAnalyzer):
    """Class to fit all linear models"""

    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.Model = None
        self.coeffs = None
        self.y_variable = None

    def analyze(
        self,
        vars: list[str] = list(BaseAnalyzer.varformatdict.keys()),
        y_variable="duration",
        **kwargs,
    ):
        super().analyze(vars=vars, y_variable=y_variable, **kwargs)
        if self.model is None:
            log.warning("no model fitted, cannot analyze")
            return
        coeffs = pd.DataFrame([self.dummycols, pd.Series(self.model.coef_)]).T
        interc = pd.DataFrame([["intercept", self.model.intercept_]])
        self.coeffs = pd.concat([coeffs, interc], axis=0)
        self.coeffs = self.coeffs.rename({0: "variable", 1: "value"}, axis=1)

    def dash_output(self):
        if self.coeffs is None:
            log.warning("dash_output called before analyze method, coeffs undefined")
            return "no results generated yet"
        datatable = dash_table.DataTable(
            columns=[
                {"name": "Flag variable", "id": "variable", "type": "text"},
                {
                    "name": "Value",
                    "id": "value",
                    "type": "numeric",
                    "format": dict(specifier="+.2f"),
                },
            ],
            data=self.coeffs.to_dict("records"),
            filter_action="native",
            filter_query="{value} s> 0.00001 || {value} s<-00000.1",
            style_header={"font-weight": "bold", "background-color": "var(--bs-card-cap-bg)"},
            style_filter={"display": "none", "height": "0px"},
        )
        plot_predicted_vs_true = self.plot_predicted_vs_true()
        tabs = dbc.Tabs(
            [
                dbc.Tab(
                    html.Div(
                        [
                            html.Div(f"{len(self.d)} data points used (outliers excluded)"),
                            html.Div(
                                "Cross-validation scores: " + " ".join(["{0:3.2f}".format(x) for x in self.cvscores])
                            ),
                            datatable,
                        ]
                    ),
                    label="Coefficients",
                    tab_id="coeffs",
                ),
                dbc.Tab([plot_predicted_vs_true], label="Prediction vs. true value", tab_id="plot"),
            ],
            active_tab="plot",
        )
        return tabs


class AnalyzeLasso(AnalyzeLinear):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.Model = linear_model.Lasso

    @staticmethod
    def dash_inputs_args(id):
        return [dbc.Input(value=0.1, type="number", min=0, max=1, step=0.1, id=id | {"id": "alpha"})]


class AnalyzeLassoCV(AnalyzeLinear):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.Model = linear_model.LassoCV

    @staticmethod
    def dash_inputs_args(id):
        return [dbc.Input(value=5, type="number", min=2, max=10, step=1, id=id | {"id": "cv"})]


class AnalyzeRidge(AnalyzeLinear):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.Model = linear_model.Ridge

    @staticmethod
    def dash_inputs_args(id):
        return [dbc.Input(value=0.1, type="number", min=0, max=1, step=0.1, id=id | {"id": "alpha"})]


class AnalyzeRidgeCV(AnalyzeLinear):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.Model = linear_model.RidgeCV

    @staticmethod
    def dash_inputs_args(id):
        return [dbc.Input(value="(0.1,1.0,10.0)", type="text", id=id | {"id": "eval_alphas"})]


def make_callback_decs(analyzerid):
    return [
        Output({"component": "analyzerresult", "analyzerid": analyzerid}, "children"),
        Input({"component": "analyzerinputs", "analyzerid": analyzerid, "id": ALL}, "value"),
        Input({"component": "analyzerinputs", "analyzerid": analyzerid, "id": ALL}, "id"),
        Input("storedflag", "data"),
        State("sessionid", "data"),
        Input("cluster_dropdown", "value"),
        Input("target_variable_dropdown", "value"),
    ]


@callback(
    *make_callback_decs("AnalyzeLasso"),
    prevent_initial_call=True,
)
def callback_lasso(values, ids, storedflag, sessionid, cluster, y_variable):
    return callback_linear(values, ids, storedflag, sessionid, cluster, y_variable)

@callback(
    *make_callback_decs("AnalyzeLassoCV"),
    prevent_initial_call=True,
)
def callback_lassocv(values, ids, storedflag, sessionid, cluster, y_variable):
    return callback_linear(values, ids, storedflag, sessionid, cluster, y_variable)

@callback(
    *make_callback_decs("AnalyzeRidge"),
    prevent_initial_call=True,
)
def callback_ridge(values, ids, storedflag, sessionid, cluster, y_variable):
    return callback_linear(values, ids, storedflag, sessionid, cluster, y_variable)

@callback(
    *make_callback_decs("AnalyzeRidgeCV"),
    prevent_initial_call=True,
)
def callback_ridgecv(values, ids, storedflag, sessionid, cluster, y_variable):
    return callback_linear(values, ids, storedflag, sessionid, cluster, y_variable)

def callback_linear(values, ids, storedflag, sessionid, cluster, y_variable):
    if not storedflag or len(ids) == 0 or len(cluster) == 0:
        return no_update
    log.debug(f"callback linear: values = {values} ids = {ids} cluster = {cluster} ")
    analyzerid = ids[0].get("analyzerid")
    log.info(f"callback linear analyzerid = {analyzerid}")
    ids = [x.get("id") for x in ids]
    kwargs = dict(zip(ids, values))
    kwargs = {
        (k[5:] if k.startswith("eval_") else k): (eval(v) if k.startswith("eval_") else v) for k, v in kwargs.items()
    }
    log.debug(f"callback linear kwargs = {kwargs}")
    if None in kwargs.values():
        log.warning("callback linear called with missing arguments")
        return no_update
    dr, _ = get_data_from_pickle_session(sessionid)
    dr = get_prepared_data(dr, cluster=cluster)
    a = eval(analyzerid)(dr)
    a.analyze(y_variable=y_variable, **kwargs)
    return a.dash_output()
