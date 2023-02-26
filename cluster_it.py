"""
Functions to cluster routers
"""
from hdbscan import HDBSCAN
import numpy as np
import pandas as pd
from typing import Optional
from scipy.cluster.hierarchy import average, fcluster
from scipy.spatial.distance import squareform
from sklearn.metrics.pairwise import pairwise_distances
import logging

log = logging.getLogger("gpxfun." + __name__)


def calc_cluster_from_dist(
    distm,
    indices: list,
    clusterlabel: str = "cluster",
    min_routes_per_cluster: Optional[int] = None,
):
    """
    From a distance matrix distm, calculate the clusters
    returns a pd.DataFrame with a cluster label for each index in indices
    cluster labels get suffix given in clusterlabel
    :param distm: distance matrix must be of shape (len(indices),len(indices))
    """
    # confusing: squareform transforms to upperdiagmatrix when called on a square matrix
    updiagm = squareform(distm)
    Z = average(updiagm)
    cluster_labels = fcluster(Z, np.quantile(updiagm, 0.3), criterion="distance")
    # reorder cluster labels according to size of cluster
    dfcluster = pd.DataFrame(
        zip(indices, cluster_labels),
        columns=["dateiname", "cluster"],
    )
    x = (
        dfcluster.cluster
        .value_counts()
        .sort_values(ascending=False)
        .reset_index()
        .rename({"index": "old"}, axis=1)
        .reset_index()
        .rename({"index": "new"}, axis=1)
    )
    if min_routes_per_cluster is not None:

        def only_large(r):
            if r["cluster"] > min_routes_per_cluster:
                return r["new"]
            else:
                return "other"

        x["new"] = x.apply(only_large, axis=1)
    x = (
        x
        .drop("cluster", axis=1)
        .rename({"old":"cluster"}, axis=1)
    )
    x.new = [clusterlabel + "_" + str(r) for r in x.new]
    dfcluster = (
        pd.merge(dfcluster, x, on="cluster")
        .drop("cluster", axis=1)
        .rename({"new": "cluster"}, axis=1)
    )
    dfcluster.index = dfcluster.dateiname
    # labls = dfcluster.cluster.unique()
    # print(f"For {clusterlabel}, {len(labls)} Clusters: {labls}")
    return dfcluster


def cluster_all(
    d: pd.DataFrame,
    dists: dict,
    most_imp_clusters: pd.DataFrame,
    min_routes_per_cluster: Optional[int] = None,
):
    log.info("cluster {len(d)} routes in {len(most_imp_clusters)} startendclusters")
    """Cluster routes grouped by custom locations and write to disk"""
    d["cluster"] = ""
    d.index = d.dateiname
    for a in list(most_imp_clusters.startendcluster.cat.categories):
        dfcluster = calc_cluster_from_dist(
            dists[a],
            dists[str(a) + "_dateinamen"],
            clusterlabel=str(a),
            min_routes_per_cluster=min_routes_per_cluster,
        )
        d.update(dfcluster, join="left")
    d = d.reset_index(drop=True)
    clustercombis = (
        d.groupby(["startendcluster", "cluster"])["dateiname"].count().reset_index()
    )
    clustercombis = clustercombis[clustercombis.dateiname > 0]
    clustercombis = most_imp_clusters.merge(clustercombis, on="startendcluster")
    clustercombis.startendcluster.astype("category")
    clustercombis.cluster.astype("category")
    d["cluster"] = d.cluster.astype("category")
    return d, clustercombis


def cluster_it(
    distm,
    dateinamen: list,
    clusterlabel: str = "cluster",
    min_cluster_size: int = 5,
) -> pd.DataFrame:
    """Finds cluster in a distance matrix"""
    distsm = pairwise_distances(distm)
    # clusterer = DBSCAN(eps=2E-4,metric="precomputed")
    clusterer = HDBSCAN(
        metric="precomputed",
        min_cluster_size=min_cluster_size,
        algorithm="best",
        approx_min_span_tree=False,
        allow_single_cluster=True,
    )
    cluster_labels = clusterer.fit_predict(distsm)
    # print(
    #     f"Für {clusterlabel} habe ich folgende {len(list(set(cluster_labels)))} Cluster gefunden: {list(set(cluster_labels))}"
    # )
    dfcluster = pd.DataFrame(
        zip(dateinamen, [clusterlabel + "_" + str(x) for x in cluster_labels]),
        columns=["dateiname", "cluster"],
    )
    dfcluster.index = dfcluster.dateiname
    return dfcluster
