import logging
import analyzer

log = logging.getLogger("gpxfun." + __name__)


class AnalyzerFactory(object):
    """Factory class to create analyzer objects."""

    def __init__(self):
        pass

    @staticmethod
    def get_available_analyzers():
        al = [x for x in dir(analyzer) if x.startswith("Analyze")]
        log.info(f"n/o available analyzers: {len(al)}")
        return al

    avail_analyzers = get_available_analyzers()

    def get_analyzer(self, analyzerid: str):
        """ Return an analyzer object. """
        log.debug(f"get analyzer {analyzerid}")
        if analyzerid not in AnalyzerFactory.avail_analyzers:
            raise ValueError(
                f"analyzerid {analyzerid} not found in list of available"
                " analyzers. Expected one from {' '.join(self.avail_analyzers)}"
            )
        return eval("analyzer." + analyzerid)

    def get_dash_inputs(self, analyzerid: str):
        """ Return a list of dash inputs for the analyzer. """
        log.debug(f"get dash controls {analyzerid}")
        if analyzerid not in AnalyzerFactory.avail_analyzers:
            raise ValueError(
                f"analyzerid {analyzerid} not found in list of available"
                " analyzers. Expected one from {' '.join(self.avail_analyzers)}"
            )
        return eval("analyzer." + analyzerid).dash_inputs()


