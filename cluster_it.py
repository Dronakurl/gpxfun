import pandas as pd
import numpy as np
from hdbscan import HDBSCAN
from sklearn.metrics.pairwise import pairwise_distances


def cluster_it(
    distm: np.array,
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
    print(
        f"Für {clusterlabel} habe ich folgende {len(list(set(cluster_labels)))} Cluster gefunden: {list(set(cluster_labels))}"
    )
    dfcluster = pd.DataFrame(
        zip(dateinamen, [clusterlabel + "_" + str(x) for x in cluster_labels]),
        columns=["dateiname", "cluster"],
    )
    dfcluster.index = dfcluster.dateiname
    return dfcluster

# dateinamen=dists["arbeit_dateinamen"]
# distm=dists["arbeit"]
# clusterlabel="arbeit"
# min_cluster_size=3
