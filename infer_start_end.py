"""
Function to find the most common start-end-point-comibnations
"""
import numpy as np
import logging
import pandas as pd
from scipy.cluster.hierarchy import average, fcluster
from scipy.spatial.distance import pdist
from typing import Tuple
from gpxpy.geo import Location

log = logging.getLogger("gpxfun." + __name__)

def infer_start_end(
    df: pd.DataFrame,
    quantile_for_cluster: float = 0.15,
    max_no_clusters: int = 4,
    infer_by_distance: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Start and stop locations are put in a 4D array for clustering.
    (latitude and longitude of start (2 dimensions) + same for end point
    the most common start and endpoint combinations are marked
    :param df: Pandas DataFrame with start and stop columns containing gpxpy.geo.Location 
                objects or any objects that have latitude and longitude attributes
    :type df: pandas.DataFrame
    :param quantile_for_cluster: Quantile of the distance distribution that is 
                    used to determine the clusters
    :type quantile_for_cluster: float
    :param max_no_clusters: maximal number of clusters to be inferred
    :type max_no_clusters: int
    :param infer_by_distance: If True, additionally infer the clusters from the algorithm
                    and just get all points within 150m of the center of each cluster
    :type infer_by_distance: bool
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
    most_imp_clust = d.startendcluster.value_counts()
    # at least 3 routes per cluster
    most_imp_clust = most_imp_clust[most_imp_clust > 2]
    # a maximum of max_no_clusters clusters is chosen
    most_imp_clust = (
        most_imp_clust.head(max_no_clusters)
        .reset_index()
        .drop("startendcluster", axis=1)
        .rename({"index": "old"}, axis=1)
        .reset_index()
        .rename({"index": "startendcluster"}, axis=1)
    )
    most_imp_clust["startendcluster"] = most_imp_clust.startendcluster.astype(
        "category"
    )
    # .cat.add_categories(-1)
    d = (
        d.rename({"startendcluster": "old"}, axis=1)
        .merge(most_imp_clust, on="old", how="left")
        .drop("old", axis=1)
    )
    # d["startendcluster"]=d.startendcluster.fillna(-1)
    most_imp_clust = (
        d.groupby(["startendcluster"])[
            ["start_lat", "start_lon", "ende_lat", "ende_lon"]
        ]
        .mean()
        .reset_index()
    )

    most_imp_clust["start"] = most_imp_clust.apply(
        lambda x: Location(x["start_lat"], x["start_lon"], None), axis=1
    )
    most_imp_clust["ende"] = most_imp_clust.apply(
        lambda x: Location(x["ende_lat"], x["ende_lon"], None), axis=1
    )

    if infer_by_distance:
        tmp = most_imp_clust[["startendcluster", "start", "ende"]]
        tmp = tmp.rename(
            {
                "startendcluster": "startendcluster_x",
                "start": "start_x",
                "ende": "ende_x",
            },
            axis=1,
        )

        ds = d.copy().merge(tmp, how="cross")
        ds = ds[
            ds.apply(
                lambda x: (
                    x["start"].distance_2d(x["start_x"]) < 150
                    and x["ende"].distance_2d(x["ende_x"]) < 150
                ),
                axis=1,
            )
        ][["startendcluster", "startendcluster_x", "dateiname"]]

        d = d.merge(ds[["dateiname", "startendcluster_x"]], how="left").rename(
            {
                "startendcluster": "startendcluster_algo",
                "startendcluster_x": "startendcluster",
            },
            axis=1,
        )

        da = d[["startendcluster", "startendcluster_algo", "dateiname"]].copy()
        da["startendcluster"] = da.startendcluster.cat.add_categories(-1).fillna(-1)
        da["startendcluster_algo"] = da.startendcluster_algo.cat.add_categories(
            -1
        ).fillna(-1)
        if log.level==logging.DEBUG:
            print(
                pd.pivot_table(
                    da,
                    "dateiname",
                    index="startendcluster",
                    columns="startendcluster_algo",
                    aggfunc="count",
                )
            )

    if log.level==logging.DEBUG:
        da=d[["dateiname","startendcluster"]].copy()
        da["startendcluster"] = da.startendcluster.cat.add_categories(-1).fillna(-1)
        print("infer_start_end: final cluster statistics")
        print(pd.pivot_table(da, "dateiname", index="startendcluster", aggfunc="count"))

    return d, most_imp_clust
