import pandas as pd
from dash import dcc, html
import dash_bootstrap_components as dbc

class AnalyzeModel(object):
    def __init__(self, data: pd.DataFrame):
        self.d = data

    def analyze(self):
        pass

    def output(self):
        return "Test Output"

    def dash_settings(self):
        return html.Div("Wurst")

    def dash_results(self):
        return html.Div(self.output())
