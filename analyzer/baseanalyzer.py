import pandas as pd
import plotly.express as px
import logging

from dash import dcc, html
from prepare_data import y_variables_dict
from sklearn.model_selection import cross_val_score, train_test_split

log = logging.getLogger("gpxfun." + __name__)


varformatdict = {
    "season": "Season",
    "weekday": "Weekday",
    "cluster": "Route cluster",
    "startendcluster": "Start/end cluster",
    "starttime": "Start time",
    "temp": "Temperature",
}


class BaseAnalyzer(object):
    varformatdict = varformatdict

    def __init__(self, data: pd.DataFrame):
        self.d = data

    def analyze(self):
        pass

    def analyze(
        self,
        vars: list[str] = list(varformatdict.keys()),
        y_variable="duration",
        **kwargs,
    ):
        # data preparation
        ds = self.d[vars]
        self.y_variable = y_variable
        num_cols = list(ds.columns[ds.dtypes.isin((int, float))])
        cat_cols = list(ds.columns[~ds.dtypes.isin((int, float))])
        log.debug(f"numeric columns: {num_cols}, categorical: {cat_cols}")
        if len(num_cols) > 0:
            log.error("cannot deal with numeric data yet. scaling and stuff")
        X = pd.get_dummies(ds)
        self.dummycols = pd.Series(X.columns)
        y = self.d[y_variable]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
        # train the model
        model = self.Model(**kwargs)
        model.fit(X_train, y_train)
        # an idea for GridSearchCV
        # parameters = {'kernel':('linear', 'rbf', 'poly'), 'degree':(2,3,4), 'C':[1, 10]}
        # clf=GridSearchCV(model,parameters)
        # clf.fit(X_train,y_train)
        # model=clf.best_estimator_
        # model.fit(X_train,y_train)
        # yp=model.predict(X_test)
        # apply to test dataset
        y_test_p = model.predict(X_test)
        y_test = y_test.rename("y_test")
        y_test = pd.merge(y_test, self.d["filename"], left_index=True, right_index=True)
        y_test_p = pd.Series(y_test_p, index=y_test.index, name="y_test_p")
        self.test_y = pd.concat([y_test, y_test_p], axis=1)
        self.cvscores = cross_val_score(model, X, y, cv=5)
        self.model = model

    def output(self):
        return "Test Output"

    def dash_output(self):
        return "Test Output"

    @classmethod
    def dash_inputs(cls):
        return ""

    @classmethod
    def dash_inputs(cls, includevars: bool = True):
        log.debug(f"dash_inputs for class {cls.__name__}")
        id = {"component": "analyzerinputs", "analyzerid": cls.__name__}
        vars_checklist = [
            dcc.Checklist(
                options=BaseAnalyzer.varformatdict,
                value=list(BaseAnalyzer.varformatdict.keys()),
                id=id | dict(id="vars"),
                # labelClassName="blocky",
                labelStyle={"display": "block"},
                inputStyle={"display": "inline", "padding-right": "20px"},
            )
        ]
        if not includevars:
            vars_checklist = []
        return html.Div(vars_checklist + cls.dash_inputs_args(id))

    @staticmethod
    def dash_inputs_args(id):
        log.debug(f"empty dash_inputs_args called with id = {id}")
        return []

    def plot_predicted_vs_true(self):
        fig = px.scatter(self.test_y, height=300, x="y_test", y="y_test_p")
        yvar = y_variables_dict.get(self.y_variable, "y_variable")
        fig.update_layout(xaxis_title=f"true {yvar}", yaxis_title=f"predicted {yvar}"),
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        plot_predicted_vs_true = dcc.Graph(figure=fig)
        return plot_predicted_vs_true
