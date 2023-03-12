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
import plotly.express as px
from sklearn import linear_model

from app_data_functions import get_data_from_pickle_session
from prepare_data import get_prepared_data
from sklearn.model_selection import cross_val_score, train_test_split, cross_val_predict, GridSearchCV
from prepare_data import y_variables_dict

from .analyzemodel import BaseAnalyzer


log = logging.getLogger("gpxfun." + __name__)


class AnalyzeLinear(BaseAnalyzer):
    """Class to fit all linear models"""

    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.Model = None
        self.coeffs = None
        self.y_variable=None

    def analyze(
        self,
        vars: list[str] = list(BaseAnalyzer.varformatdict.keys()),
        y_variable="duration",
        **kwargs,
    ):
        ds = self.d[vars]
        self.y_variable=y_variable
        X = pd.get_dummies(ds)
        dummycols = pd.Series(X.columns)
        y = self.d[y_variable]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
        if not hasattr(self, "Model"):
            log.warning("analyze called without model object, abort")
            return
        model = self.Model(**kwargs)
        model.fit(X_train, y_train)
        coeffs = pd.DataFrame([dummycols, pd.Series(model.coef_)]).T
        interc = pd.DataFrame([["intercept", model.intercept_]])
        self.coeffs = pd.concat([coeffs, interc], axis=0)
        self.coeffs = self.coeffs.rename({0: "variable", 1: "value"}, axis=1)
        y_test_p = model.predict(X_test)
        y_test= y_test.rename("y_test")
        y_test=pd.merge(y_test,self.d["filename"],left_index=True,right_index=True)
        y_test_p = pd.Series(y_test_p,index=y_test.index,name="y_test_p")
        self.test_y = pd.concat([y_test, y_test_p],axis=1)
        self.cvscores = cross_val_score(model, X, y, cv=5)

    @staticmethod
    def dash_inputs_args(id):
        log.debug(f"empty dash_inputs_args called with id = {id}")
        return []

    @classmethod
    def dash_inputs(cls):
        log.debug(f"dash_inputs for class {cls.__name__}")
        id = {"component": "linearinputs", "analyzerid": cls.__name__}
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
        fig=px.scatter(self.test_y, height=300, x="y_test", y="y_test_p")
        yvar=y_variables_dict.get(self.y_variable,'y_variable')
        fig.update_layout( xaxis_title=f"true {yvar}", yaxis_title=f"predicted {yvar}"),
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        plot_predicted_vs_true = dcc.Graph(figure=fig)
        tabs = dbc.Tabs(
            [
                dbc.Tab(
                    html.Div(
                        [
                            html.Div(f"{len(self.d)} data points used (outliers excluded)"),
                            html.Div("Cross-validation scores: " + " ".join(["{0:3.2f}".format(x) for x in self.cvscores])),
                            datatable,
                        ]
                    ),
                    label="Coefficients",tab_id="coeffs"
                ),
                dbc.Tab([plot_predicted_vs_true], label="Prediction vs. true value",tab_id="plot")
            ]
            ,active_tab="plot"
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


@callback(
    Output({"component": "analyzerresult", "analyzerid": MATCH}, "children"),
    Input({"component": "linearinputs", "analyzerid": MATCH, "id": ALL}, "value"),
    Input({"component": "linearinputs", "analyzerid": MATCH, "id": ALL}, "id"),
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
