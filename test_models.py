from app_data_functions import get_data_from_pickle_session
from prepare_data import get_data_for_one_startend
from analyzer_factory import AnalyzerFactory

dr, _ = get_data_from_pickle_session("test")
dr = get_data_for_one_startend(dr, startendcluster=0)
a = AnalyzerFactory().get_analyzer("AnalyzeLasso")(dr)
a.analyze()

print(a.coeffs)
