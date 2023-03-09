import logging

import pandas as pd
from sklearn.neighbors import LocalOutlierFactor
from typing import Union

log = logging.getLogger("gpxfun." + __name__)


def get_data_for_one_startend(
    d: pd.DataFrame, startendcluster: Union[int, list] = 1, minrecords: int = 10
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
    if isinstance(startendcluster, int):
        startendcluster = [startendcluster]
    startendcluster = [int(x) for x in startendcluster]
    dr = d[d.startendcluster.isin(startendcluster)].copy()
    log.info(f"Filter {len(d)} points to secluster {startendcluster} -> {len(dr)} points")
    clustercounter = dr.cluster.value_counts().sort_values(ascending=False)
    imp_clusters = list(clustercounter[clustercounter >= minrecords].index)
    dr.cluster = dr.cluster.apply(lambda x: x if x in imp_clusters else "other")
    dr["startzeitnum"] = dr.startzeit.apply(lambda x: x.hour + x.minute / 60.0)
    dr["startzeit"] = pd.cut(dr.startzeitnum, 4)
    dr["temp"] = pd.cut(dr.temp, 4)
    return dr


def exclude_outliers(dr: pd.DataFrame, cols: list[str] = ["dauer"]) -> pd.DataFrame:
    """
    remove outliers of an input DataFrame
    :param dr: pandas DataFrame, containing all columns in cols
    :param cols: columns in DataFrame dr which are used for outlier detection, must be numeric
    """
    do = mark_outliers(dr, cols=cols)
    return do[do.is_outlier == False].drop("is_outlier", axis=1)


def mark_outliers(dr: pd.DataFrame, cols: list[str] = ["dauer"]) -> pd.DataFrame:
    """
    Detect outliers of an input DataFrame
    :param dr: pandas DataFrame, containing all columns in cols
    :param cols: columns in DataFrame dr which are used for outlier detection, must be numeric
    """
    if len(dr) == 0:
        return dr.copy()
    clf = LocalOutlierFactor(n_neighbors=int(len(dr) * 0.8))
    y = pd.Series(clf.fit_predict(dr[cols]) == -1, index=dr.index).astype("bool")
    do = dr.copy()
    do["is_outlier"].update(y)
    log.info(f"records: {len(dr)}, outliers: {do.is_outlier.value_counts().to_dict().get(True,'0')}")
    for x in do[do.is_outlier].index:
        log.debug(f"outlier in dateiname:{do.loc[x,'dateiname']}, dauer:{do.loc[x,'dauer']}")
    return do


def mark_outliers_per_cluster(
    dr: pd.DataFrame, cols: list[str] = ["dauer"], clustercol: str = "startendcluster"
) -> pd.DataFrame:
    """
    Detect outliers in an input dataframe, in clusters marked by the column in clustercol
    :param dr: input DataFrame, containing all columns in clos
    :param cols: List of columns that should be used in outlier detection
    :parm clustercol: Column in dr. For each different value of clustercol, outliers are detected
    """
    do = dr.copy()
    do_a = do[do[clustercol].notna()].copy()
    do_b = do[~do[clustercol].notna()]
    do_a["is_outlier"] = False
    do_a = do_a.groupby(by=clustercol, group_keys=False).apply(mark_outliers, cols=cols)
    # do_a_new=pd.DataFrame()
    # for clusterval in list(set(list(do_a[clustercol]))):
    #     y=mark_outliers(do_a[do_a[clustercol]==clusterval],cols=cols)
    #     do_a_new=pd.concat([do_a_new,y])
    # do_a=do_a_new
    do = pd.concat([do_a, do_b], axis=0)
    do["is_outlier"] = do["is_outlier"].fillna(False).astype("bool")
    return do
