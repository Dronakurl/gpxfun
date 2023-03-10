import pandas as pd
import logging

log = logging.getLogger("gpxfun." + __name__)


varformatdict = {
    "season": "Season",
    "weekday": "Weekday",
    "cluster": "Route cluster",
    "startendcluster": "Start/end cluster",
    "starttime": "Start time",
    "temp": "Temperature",
}

class AnalyzeModel(object):
    varformatdict = varformatdict 
    def __init__(self, data: pd.DataFrame):
        self.d = data

    def analyze(self):
        pass

    def output(self):
        return "Test Output"

    def dash_output(self):
        return "Test Output"

    def dash_inputs():
        return ""

