""" 
Function to handle the pickle data for each session 
to be used within the main dash app.py
"""
from pathlib import Path
import pickle
from typing import Tuple
import logging

import pandas as pd

from gpxfun.calc_dist_matrix import calc_dist_matrix_per_se_cluster
from gpxfun.cluster_it import cluster_all
from gpxfun.infer_start_end import infer_start_end
from gpxfun.parse_gpx import update_pickle_from_folder
from gpxfun.prepare_data import mark_outliers_per_cluster

log = logging.getLogger("gpxfun." + __name__)


def parse_and_cluster(
    infolder: str,
    mypickle: Path = Path("pickles/df.pickle"),
    delete: bool = False,
    y_variable: str = "duration"
) -> pd.DataFrame:
    """
    1. Parse the gpx data in a folder to a data frame
    2. Get weather data from meteostat
    3. Infer startend cluster (most common start end points) -> startendcluster column
    4. Find the most common routes for each startendcluster -> cluster column
    5. Save output data frame to pickle file
    :param infolder: input folder for gpx data
    :param mypickle: Path of the pickle file to store the output
    :param delete: True if the gpx files should be deleted after they are read
    :return: DataFrame with the parsed and clustered results
    """
    df = update_pickle_from_folder(infolder=infolder, mypickle=mypickle, delete=delete)
    df, se_clusters = infer_start_end(df)
    dists = calc_dist_matrix_per_se_cluster(df, simmeasure="mae")
    df, cluster_inf = cluster_all(df, dists, se_clusters, min_routes_per_cluster=10)
    df = mark_outliers_per_cluster(df, cols=[y_variable])
    log.debug(f"write df DataFrame to {mypickle}")
    with open(mypickle, "wb") as f:
        pickle.dump(df, f)
    log.debug(f"write to {Path(mypickle).parents[0] / 'most_imp_clusters.pickle'}")
    with open(Path(mypickle).parents[0] / "most_imp_clusters.pickle", "wb") as f:
        pickle.dump(cluster_inf, f)
    return df


def get_data_from_pickle_session(sessionid: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    picklefn = Path("sessions") / sessionid / "df.pickle"
    if not picklefn.is_file():
        raise ValueError(f"pickle file {picklefn} doesn't exist!")
    with open(picklefn, "rb") as f:
        df = pickle.load(f)
    with open(Path("sessions") / sessionid / "most_imp_clusters.pickle", "rb") as f:
        most_imp_clusters = pickle.load(f)
    return df, most_imp_clusters
