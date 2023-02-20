''' 
Function to handle the pickle data for each session 
to be used within the main dash app.py
'''
from pathlib import Path
import pickle
from typing import Tuple

import pandas as pd

from calc_dist_matrix import update_dist_matrix
from cluster_it import cluster_all
from infer_start_end import infer_start_end
from parse_gpx import update_pickle_from_folder

def parse_and_cluster(
    infolder: str,
    mypickle: Path = Path("pickles/df.pickle"),
    delete: bool = False,
) -> pd.DataFrame:
    """ 
    1. Parse the gpx data in a folder to a data frame 
    2. Infer startend cluster (most common start end points) -> startendcluster column
    3. Find the most common routes for each startendcluster -> cluster column 
    4. Save output data frame to pickle file
    :param infolder: input folder for gpx data
    :param mypickle: Path of the pickle file to store the output
    :param delete: True if the gpx files should be deleted after they are read
    :return: DataFrame with the parsed and clustered results
    """
    df, updated = update_pickle_from_folder(
        infolder=infolder, mypickle=mypickle, delete=delete
    )
    df, most_imp_clusters = infer_start_end(df)
    # distance matrix is generated
    dists = update_dist_matrix(
        df,
        mypickle=Path(mypickle).parents[0] / "dists.pickle",
        updated=updated,
        simmeasure="mae",
    )
    # apply cluster algorithm for all startendcluster
    df , most_imp_clusters = cluster_all(df, dists, most_imp_clusters, writetopickle=False)
    with open(mypickle, "wb") as f:
        pickle.dump(df, f)
    with open(Path(mypickle).parents[0] / "most_imp_clusters.pickle", "wb") as f:
        pickle.dump(most_imp_clusters, f)
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

