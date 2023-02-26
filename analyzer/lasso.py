from .analyzemodel import AnalyzeModel
import pandas as pd
from sklearn import linear_model


class AnalyzeLasso(AnalyzeModel):
    def __init__(
        self,
        data: pd.DataFrame,
        alpha: float = 0.1,
        vars: list[str] = [
            "jahreszeit",
            "wochentag",
            "cluster",
            "dauer",
            "startzeit",
            # "temp",
        ],
    ):
        super().__init__(data)
        self.alpha = alpha
        self.vars = vars

    def analyze(self):
        ds = self.d[self.vars]
        X = ds.drop("dauer", axis=1)
        X = pd.get_dummies(X)
        dummycols = X.columns
        y = ds["dauer"]
        lassomodel = linear_model.Lasso(alpha=self.alpha)
        lassomodel.fit(X, y)
        self.intercept = lassomodel.intercept_
        self.coeffs = pd.DataFrame([dummycols, pd.Series(lassomodel.coef_)]).T

    def output(self):
        return self.intercept
