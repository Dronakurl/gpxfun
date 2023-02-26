import logging

import pandas as pd
from sklearn.neighbors import LocalOutlierFactor

log = logging.getLogger(__name__)


def get_data_for_one_startend(
    d: pd.DataFrame, startendcluster: int = 1, minrecords: int = 10
) -> pd.DataFrame:
    """
    Filter the data of one startendcluster and apply data transformations needed for
    statistical analysis
    :param d: pandas DataFrame with the data
    :type d: pandas.DataFrame
    :param startendcluster: id of the startendcluster
    :param minrecords: minimum number of records for each route cluster,
                route clusters with less amount of records are put into "other" cluster
    """
    dr = d[d.startendcluster == startendcluster].copy()
    log.info(
        f"Filter {len(d)} points to secluster {startendcluster} -> {len(dr)} points"
    )
    clustercounter = dr.cluster.value_counts().sort_values(ascending=False)
    imp_clusters = list(clustercounter[clustercounter >= minrecords].index)
    dr.cluster = dr.cluster.apply(lambda x: x if x in imp_clusters else "other")
    dr["startzeitnum"] = dr.startzeit.apply(lambda x: x.hour + x.minute / 60.0)
    dr["startzeit"] = pd.cut(dr.startzeitnum, 4)
    dr["temp"] = pd.cut(dr.temp, 4)
    return dr


def exclude_outliers(dr: pd.DataFrame, cols: list[str] = ["dauer"]) -> pd.DataFrame:
    clf = LocalOutlierFactor(n_neighbors=int(len(dr) * 0.8))
    y = clf.fit_predict(dr[cols])
    y = pd.DataFrame(y, columns=["outliers"])
    yX = pd.concat([y, dr[cols].reset_index(drop=False)], axis=1)
    do = dr.loc[yX[yX.outliers > 0]["index"]]
    log.info(f"number of input records {len(dr)} -> output {len(do)}")
    return do
    # px.scatter(yX, x="dauer", y="startzeitnum", color="outliers")
    # clf.negative_outlier_factor_
