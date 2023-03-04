import pandas as pd
import logging
import analyzer

log = logging.getLogger("gpxfun." + __name__)


class AnalyzerFactory(object):
    def __init__(self, data: pd.DataFrame):
        self.avail_analyzers = self.get_available_analyzers()
        self.d = data

    def get_available_analyzers(self):
        al = [x for x in dir(analyzer) if x.startswith("Analyze")]
        log.info(f"n/o available analyzers: {len(al)}")
        return al

    def get_analyzer(self, analyzerid: str):
        log.debug(f"get analyzer {analyzerid}")
        return eval("analyzer." + analyzerid)(self.d)


if __name__ == "__main__":
    from mylog import get_log
    log = get_log()
    af = AnalyzerFactory(pd.DataFrame())
    print("\n".join(af.avail_analyzers))
