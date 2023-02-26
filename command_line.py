"""
A script to prepare the data and test plots for gpx analysis
"""
import logging
from pathlib import Path
import pickle

import pandas as pd

from analyzer_factory import AnalyzerFactory
from calc_dist_matrix import update_dist_matrix
from cluster_it import cluster_all
from infer_start_end import infer_start_end
from mylog import get_log
from parse_gpx import update_pickle_from_folder
from prepare_data import exclude_outliers, get_data_for_one_startend

log = get_log("gpxfun", logging.DEBUG)

log.info("start")
# Read the gpx data from a folder. Data is stored in y pickle, so that
# it does not need to be reloaded every time.
d, updated = update_pickle_from_folder(
    infolder="/home/konrad/gpxfun/data",
    mypickle=Path("sessions/testcli/df.pickle"),
    weather=True,
)

# infer common start end points
d, most_imp_clusters = infer_start_end(d, max_no_clusters=2)

# distance matrix is generated, if not already stored in a pickle
dists = update_dist_matrix(
    d, mypickle=Path("sessions/testcli/dists.pickle"), updated=updated
)

# Apply Cluster algorithm to get similar paths
d, most_imp_clusters = cluster_all(
    d, dists, most_imp_clusters, min_routes_per_cluster=10
)

mypickle = Path("sessions/testcli/df.pickle")
log.debug(f"write df DataFrame to {mypickle}")
with open(mypickle, "wb") as f:
    pickle.dump(d, f)
log.debug(
    f"write df DataFrame to {Path(mypickle).parents[0] / 'most_imp_clusters.pickle'}"
)
with open(Path(mypickle).parents[0] / "most_imp_clusters.pickle", "wb") as f:
    pickle.dump(most_imp_clusters, f)

log.info("Data is ready, show Number of clusters")
log.info(
    pd.pivot_table(
        d,
        "dateiname",
        index=["startendcluster"],
        aggfunc=["count"],
        margins=True,
    )
)

dr = get_data_for_one_startend(d, startendcluster=1)
dr = exclude_outliers(dr)


afactory = AnalyzerFactory(dr)
lasso = afactory.get_analyzer("AnalyzeLasso")
lasso.analyze()
print(lasso.output())
