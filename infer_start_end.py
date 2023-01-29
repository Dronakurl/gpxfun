"""
Function to find the most common start-end-point-comibnations
"""
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import average, fcluster
from scipy.spatial.distance import pdist
from typing import Tuple


def infer_start_end(
    df: pd.DataFrame, quantile_for_cluster: float = 0.15
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Start and stop locations are put in a 4D array for clustering.
    (latitude and longitude of start (2 dimensions) + same for end point
    the most common start and endpoint combinations are marked
    """
    d = df.copy()
    startstop4d = d.apply(
        lambda x: [
            x["start"].latitude,
            x["start"].longitude,
            x["ende"].latitude,
            x["ende"].longitude,
        ],
        axis=1,
    )
    coordsstartend = pd.DataFrame(
        startstop4d.to_list(),
        columns=["start_lat", "start_lon", "ende_lat", "ende_lon"],
    )
    d = pd.concat([d, coordsstartend], axis=1)
    dists = pdist(np.array(startstop4d.to_list()))
    cluster_labels = fcluster(
        average(dists), np.quantile(dists, quantile_for_cluster), criterion="distance"
    )
    d["startendcluster"] = pd.Series(cluster_labels)
    most_imp_clust = (
        d.startendcluster.value_counts()
        .head(4)
        .reset_index()
        .drop("startendcluster", axis=1)
        .rename({"index": "old"}, axis=1)
        .reset_index()
        .rename({"index": "startendcluster"}, axis=1)
    )
    most_imp_clust["startendcluster"] = most_imp_clust.startendcluster.astype(
        "category"
    )
    d = (
        d.rename({"startendcluster": "old"}, axis=1)
        .merge(most_imp_clust, on="old", how="left")
        .drop("old", axis=1)
    )
    most_imp_clust = d.groupby(["startendcluster"])[[
        "start_lat", "start_lon", "ende_lat", "ende_lon"
    ]].mean().reset_index()
    return d, most_imp_clust

