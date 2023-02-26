import pandas as pd
import logging
import analyzer

log = logging.getLogger("gpxfun."+__name__)

class AnalyzerFactory(object):
    def __init__(self, data: pd.DataFrame):
        self.avail_analyzers = self.get_available_analyzers()
        self.d = data

    def get_available_analyzers(self):
        al=[x for x in dir(analyzer) if x.startswith("Analyze")]
        return al

    def get_analyzer(self,analyzerid:str):
        return eval("analyzer."+analyzerid)(self.d)
        

