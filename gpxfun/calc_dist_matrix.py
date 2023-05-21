"""
Provides functions to calculate distance matrices with different measures
"""
from math import sqrt
import logging

import numpy as np
import pandas as pd
import similaritymeasures
from tqdm import tqdm

log = logging.getLogger("gpxfun." + __name__)


def area_comp(x: list, y: list):
    return convert_to_np_and_compare(x, y, similaritymeasures.area_between_two_curves)


def mae(x: list, y: list):
    return convert_to_np_and_compare(x, y, similaritymeasures.mae)


def mse(x: list, y: list):
    return convert_to_np_and_compare(x, y, similaritymeasures.mse)


def convert_to_np_and_compare(x: list, y: list, simmeasure):
    xx = np.array([np.array(xx) for xx in x])
    yy = np.array([np.array(xx) for xx in y])
    return simmeasure(xx, yy)


def euclidean(x, y):
    return sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)


def calc_dist_matrix(
    df: pd.DataFrame,
    simmeasure: str = "mae",
    compvar: str = "route_inter",
) -> np.ndarray:
    distance_mat = np.full((len(df), len(df)), -9999.0)
    smeasures = {"mae": mae, "mse": mse, "area_comp": area_comp}
    sim_fun = smeasures.get(simmeasure)
    if sim_fun is None:
        raise ValueError(f"calc_dist_matrix: simmeasure {simmeasure} unknown")
    matrix_indices = [(xi, yi) for xi in range(len(df)) for yi in range(len(df))]
    for mindex in tqdm(matrix_indices, colour="#00ffff", desc="calc dist matrix"):
        xi, yi = mindex
        if yi > xi:
            distance_mat[xi, yi] = sim_fun(df.iloc[xi][compvar], df.iloc[yi][compvar])
            distance_mat[yi, xi] = distance_mat[xi, yi]
        elif yi == xi:
            distance_mat[xi, yi] = 0
    return distance_mat




def calc_dist_matrix_per_se_cluster(d: pd.DataFrame, simmeasure: str = "mae") -> dict:
    """
    Look for the given pickle file and update it with the distance
    matrix if necessary, i.e. if the updated flag is set
    :return : dictionary with the distance matrix and the indices (column filename) for each startendcluster
    """
    dists = {}
    startendclusters = list(d.startendcluster.cat.categories)
    log.debug(f"distance mat clusters: {' '.join([str(x) for x in startendclusters])}")
    for a in startendclusters:
        log.info(f"distance matrix for routes in startendcluster {a}")
        dsub = d[d.startendcluster == a]
        dists[str(a) + "_filenamen"] = list(dsub.loc[:, "filename"])
        dists[a] = calc_dist_matrix(dsub, simmeasure=simmeasure)
    return dists
