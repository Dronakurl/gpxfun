
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
from sklearn import svm
from sklearn.model_selection import cross_val_score, train_test_split
import plotly.express as px
from prepare_data import y_variables_dict

from app_data_functions import get_data_from_pickle_session
from prepare_data import get_prepared_data

from .analyzemodel import BaseAnalyzer


log = logging.getLogger("gpxfun." + __name__)

class AnalyzeSVR(BaseAnalyzer):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.Model = svm.SVR

    def analyze(
        self,
        vars: list[str] = list(BaseAnalyzer.varformatdict.keys()),
        y_variable="duration",
        **kwargs,
    ):
        ds = self.d[vars]
        num_cols=list(ds.columns[ ds.dtypes.isin((int,float))])
        cat_cols=list(ds.columns[~ds.dtypes.isin((int,float))])
        log.debug(f"numeric columns: {num_cols}, categorical: {cat_cols}")
        if len(num_cols)>0:
            log.error("cannot deal with numeric data yet. scaling and stuff")
        X = pd.get_dummies(ds)
        y = self.d[y_variable]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
        model=svm.SVR(**kwargs)
        model.fit(X_train,y_train)
        y_test_p = model.predict(X_test)
        y_test= y_test.rename("y_test")
        y_test=pd.merge(y_test,self.d["filename"],left_index=True,right_index=True)
        y_test_p = pd.Series(y_test_p,index=y_test.index,name="y_test_p")
        self.test_y = pd.concat([y_test, y_test_p],axis=1)
        self.cvscores = cross_val_score(model, X, y, cv=5)

    @staticmethod
    def dash_inputs_args(id):
        kerneldict = {"rbf": "RBF", "linear": "Linear", "poly": "Polynomial"}
        dashin=[]
        dashin = +[dbc.Checklist(options=kerneldict, value="rbf", id=id | {"id": "C"})]
        dashin = +[dbc.Input(value=None, type="text", id=id | {"id": "gamma"})]
        dashin = +[dbc.Input(value=None, type="text", id=id | {"id": "epsilon"})]
        return dashin

    def dash_output(self):
        if self.coeffs is None:
            log.warning("dash_output called before analyze method, coeffs undefined")
            return "no results generated yet"
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
                        ]
                    ),
                    label="Coefficients",tab_id="coeffs"
                ),
                dbc.Tab([plot_predicted_vs_true], label="Prediction vs. true value",tab_id="plot")
            ]
            ,active_tab="plot"
        )
        return tabs

# @callback(
#     Output({"component": "analyzerresult", "analyzerid": MATCH}, "children"),
#     Input({"component": "svrinput", "analyzerid": MATCH}, "value"),
#     Input({"component": "svrinput", "analyzerid": MATCH}, "id"),
#     Input("storedflag", "data"),
#     State("sessionid", "data"),
#     Input("cluster_dropdown", "value"),
#     Input("target_variable_dropdown", "value"),
#     prevent_initial_call=True,
# )
# def callback_linear(values, ids, storedflag, sessionid, cluster, y_variable):
#     if not storedflag or len(ids) == 0 or len(cluster) == 0:
#         return no_update
#     log.debug(f"callback svr: values = {values} ids = {ids} cluster = {cluster} ")
#     analyzerid = ids[0].get("analyzerid")
#     log.info(f"callback svr analyzerid = {analyzerid}")
#     ids = [x.get("id") for x in ids]
#     kwargs = dict(zip(ids, values))
#     kwargs = {
#         (k[5:] if k.startswith("eval_") else k): (eval(v) if k.startswith("eval_") else v) for k, v in kwargs.items()
#     }
#     log.debug(f"callback linear kwargs = {kwargs}")
#     if None in kwargs.values():
#         log.warning("callback linear called with missing arguments")
#         return no_update
#     dr, _ = get_data_from_pickle_session(sessionid)
#     dr = get_prepared_data(dr, cluster=cluster)
#     a = eval(analyzerid)(dr)
#     a.analyze(y_variable=y_variable, **kwargs)
#     return a.dash_output()
