import logging

from dash import (
    ALL,
    Input,
    MATCH,
    Output,
    State,
    callback,
    dash_table,
    dcc,
    html,
    no_update,
)
import dash_bootstrap_components as dbc
import pandas as pd
from sklearn import linear_model

from app_data_functions import get_data_from_pickle_session
from prepare_data import get_prepared_data

from .analyzemodel import AnalyzeModel


log = logging.getLogger("gpxfun." + __name__)


class AnalyzeLinear(AnalyzeModel):
    """Class to fit all linear models"""

    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.Model = None
        self.coeffs = None

    def analyze(
        self,
        vars: list[str] = list(AnalyzeModel.varformatdict.keys()),
        y_variable="duration",
        **kwargs,
    ):
        ds = self.d[vars]
        X = pd.get_dummies(ds)
        dummycols = pd.Series(X.columns)
        y = self.d[y_variable]
        if not hasattr(self, "Model"):
            log.warning("analyze called without model object, abort")
            return
        model = self.Model(**kwargs)
        model.fit(X, y)
        coeffs = pd.DataFrame([dummycols, pd.Series(model.coef_)]).T
        interc = pd.DataFrame([["intercept", model.intercept_]])
        self.coeffs = pd.concat([coeffs, interc], axis=0)
        self.coeffs = self.coeffs.rename({0: "variable", 1: "value"}, axis=1)

    @staticmethod
    def dash_inputs_args(id):
        log.debug(f"empty dash_inputs_args called with id = {id}")
        return []

    @classmethod
    def dash_inputs(cls):
        log.debug(f"dash_inputs for class {cls.__name__}")
        id = {"component": "analyzerinputs", "analyzerid": cls.__name__}
        return html.Div(
            [
                dcc.Checklist(
                    options=AnalyzeLinear.varformatdict,
                    value=list(AnalyzeLinear.varformatdict.keys()),
                    id=id | dict(id="vars"),
                    # labelClassName="blocky",
                    labelStyle={"display": "block"},
                    inputStyle={"display": "inline", "padding-right": "20px"},
                )
            ]
            + cls.dash_inputs_args(id)
        )

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
        return html.Div([html.Div(f"{len(self.d)} data points used (outliers excluded)"),datatable])


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


@callback(
    Output({"component": "analyzerresult", "analyzerid": MATCH}, "children"),
    Input({"component": "analyzerinputs", "analyzerid": MATCH, "id": ALL}, "value"),
    Input({"component": "analyzerinputs", "analyzerid": MATCH, "id": ALL}, "id"),
    Input("storedflag", "data"),
    State("sessionid", "data"),
    Input("cluster_dropdown", "value"),
    Input("target_variable_dropdown", "value"),
    prevent_initial_call=True,
)
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
