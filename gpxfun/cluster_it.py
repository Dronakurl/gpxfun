"""
Functions to cluster routers
"""
# from hdbscan import HDBSCAN
from sklearn.cluster import DBSCAN
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
    log.debug(f"calc_cluster_from_dist {distm.shape}")
    updiagm = squareform(distm)
    Z = average(updiagm)
    cluster_labels = fcluster(Z, np.quantile(updiagm, 0.3), criterion="distance")
    # reorder cluster labels according to size of cluster
    dfcluster = pd.DataFrame(
        zip(indices, cluster_labels),
        columns=["filename", "cluster"],
    )
    x = (
        dfcluster.cluster.value_counts()
        .sort_values(ascending=False)
        .to_frame()
        .reset_index(names="old")
        .reset_index(names="new")
    )
    if min_routes_per_cluster is not None:

        def only_large(row):
            if row["count"] > min_routes_per_cluster:
                return row["new"]
            else:
                return "other"

        x["new"] = x.apply(only_large, axis=1)
    x = x.drop("count", axis=1).rename({"old": "cluster"}, axis=1)
    x.new = [clusterlabel + "_" + str(r) for r in x.new]
    dfcluster = pd.merge(dfcluster, x, on="cluster").drop("cluster", axis=1).rename({"new": "cluster"}, axis=1)
    dfcluster.index = dfcluster.filename
    # labls = dfcluster.cluster.unique()
    # print(f"For {clusterlabel}, {len(labls)} Clusters: {labls}")
    return dfcluster


def cluster_all(
    d: pd.DataFrame,
    dists: dict,
    se_clusters: pd.DataFrame,
    min_routes_per_cluster: Optional[int] = None,
):
    """Cluster routes grouped by custom locations and write to disk"""
    log.info(f"cluster_all {len(d)} routes in {len(se_clusters)} startendclusters")
    d["cluster"] = ""
    d.index = d.filename
    for a in list(se_clusters.startendcluster.cat.categories):
        dfcluster = calc_cluster_from_dist(
            dists[a],
            dists[str(a) + "_filenamen"],
            clusterlabel=str(a),
            min_routes_per_cluster=min_routes_per_cluster,
        )
        assert d.columns.duplicated().any() == False
        try:
            d.update(dfcluster, join="left")
        except:
            breakpoint()
    d = d.reset_index(drop=True)
    clustercombis = d.groupby(["startendcluster", "cluster"])["filename"].count().reset_index()
    clustercombis = clustercombis[clustercombis.filename > 0]
    clustercombis = se_clusters.merge(clustercombis, on="startendcluster")
    clustercombis.startendcluster.astype("category")
    clustercombis.cluster.astype("category")
    d["cluster"] = d.cluster.astype("category")
    return d, clustercombis


def cluster_it(distm, filenamen: list, clusterlabel: str = "cluster") -> pd.DataFrame:
    """Finds cluster in a distance matrix"""
    distsm = pairwise_distances(distm)
    clusterer = DBSCAN(eps=2e-4, metric="precomputed")
    # clusterer = HDBSCAN(
    #     metric="precomputed",
    #     min_cluster_size=min_cluster_size,
    #     algorithm="best",
    #     approx_min_span_tree=False,
    #     allow_single_cluster=True,
    # )
    cluster_labels = clusterer.fit_predict(distsm)
    dfcluster = pd.DataFrame(
        zip(filenamen, [clusterlabel + "_" + str(x) for x in cluster_labels]),
        columns=["filename", "cluster"],
    )
    dfcluster.index = dfcluster.filename
    return dfcluster
