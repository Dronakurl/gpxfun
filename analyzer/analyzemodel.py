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

    class DashOut(html.Div):
        """ These are the IDs for pattern matching in dash """
        class ids:
            mybutton = lambda aio_id: {
                "component": "DashSettings",
                "subcomponent": "mybutton",
                "aio_id": aio_id,
            }
        ids = ids

        def __init__(self, _analyzer):
            """ The Settings object contains """
            self.analyzer=_analyzer
            typeofanalyzer=self.analyzer.__class__.__name__
            log.debug(f"type of analyzer: {typeofanalyzer}")
            myin = dbc.Button("Start", id=self.ids.mybutton(typeofanalyzer))
            myout = dcc.Textarea(id=self.ids.mytextarea(typeofanalyzer), value="Wurst")
            super().__init__([myin, myout])

        # @callback(
        #     Output("analyzerresultscard", "value"),
        #     Input(ids.mybutton(MATCH), "value"),
        # )
        # def generateoutput(input):
        #     log.debug(f"CALLBACK updatetest {ctx.triggered_id}")
        #     return self

