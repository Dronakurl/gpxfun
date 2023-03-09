import pandas as pd
import logging

log = logging.getLogger("gpxfun." + __name__)


class AnalyzeModel(object):
    varformatdict = {
        "jahreszeit": "Season",
        "wochentag": "Weekday",
        "cluster": "Route cluster",
        "startendcluster": "Start/end cluster",
        "startzeit": "Start time",
        "temp": "Temperature",
    }

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

