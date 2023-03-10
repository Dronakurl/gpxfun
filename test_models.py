
from analyzer_factory import AnalyzerFactory
from app_data_functions import get_data_from_pickle_session
from mylog import get_log
from prepare_data import get_prepared_data
log = get_log("test_models", 10)
log.error("test")

dr, _ = get_data_from_pickle_session("test")
dr = get_prepared_data(dr, startendcluster=0)
a = AnalyzerFactory().get_analyzer("AnalyzeLasso")(dr)
a.analyze(alpha=0.1)
print(a.coeffs)



