import pandas as pd
from dash import dcc, html, callback, Output, Input, MATCH, ctx
import dash_bootstrap_components as dbc
import logging

log = logging.getLogger("gpxfun." + __name__)


class AnalyzeModel(object):
    def __init__(self, data: pd.DataFrame):
        self.d = data

    def analyze(self):
        pass

    def output(self):
        return "Test Output"

    class DashSettings(html.Div):
        # A set of functions that create pattern-matching callbacks of the subcomponents
        class ids:
            mybutton = lambda aio_id: {
                "component": "DashSettings",
                "subcomponent": "mybutton",
                "aio_id": aio_id,
            }
            mytextarea = lambda aio_id: {
                "component": "DashSettings",
                "subcomponent": "mytextarea",
                "aio_id": aio_id,
            }

        ids = ids

        def __init__(self, _analyzer):
            self.analyzer=_analyzer
            typeofanalyzer=self.__class__.__name__
            log.debug(f"type of analyzer: {typeofanalyzer}")
            myin = dbc.Input(id=self.ids.mybutton(typeofanalyzer))
            myout = dcc.Textarea(id=self.ids.mytextarea(typeofanalyzer), value="Wurst")
            super().__init__([myin, myout])

        @callback(
            Output(ids.mytextarea(MATCH), "value"),
            Input(ids.mybutton(MATCH), "value"),
        )
        def updatetest(input):
            log.debug(f"CALLBACK updatetest {ctx.triggered_id}")
            return input

    def dash_results(self):
        return html.Div(self.output())
