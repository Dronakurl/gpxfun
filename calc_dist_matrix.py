"""
Provides functions to calculate distance matrices with different measures
"""
from math import sqrt
from pathlib import Path
import pickle

import numpy as np
import pandas as pd
import similaritymeasures


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
    simmeasure=area_comp,
    compvar: str = "route_inter",
):
    # Um Fehler zu erkennen ein blöder Wert
    dists = np.full((len(df), len(df)), 234312992.2132)
    for xi in range(len(df)):
        for yi in range(len(df)):
            if yi > xi:
                dists[xi, yi] = simmeasure(df.iloc[xi][compvar], df.iloc[yi][compvar])
                dists[yi, xi] = dists[xi, yi]
            elif yi == xi:
                dists[xi, yi] = 0
            print(f"xi={xi} yi={yi}: {dists[xi,yi]}")
    return dists


def update_dist_matrix(
    d: pd.DataFrame, mypickle: str, updated: bool = True, simmeasure=mae
):
    if Path(mypickle).is_file() and not updated:
        with open(mypickle, "rb") as f:
            dists = pickle.load(f)
    else:
        dists = {}
        for a in ["arbeit", "heim"]:
            print(f"Berechne die Abstandsmatrix für {a}")
            dsub = d[d[a]]
            dists[a + "_dateinamen"] = list(dsub.loc[:, "dateiname"])
            dists[a] = calc_dist_matrix(dsub, simmeasure=simmeasure)
        with open(mypickle, "wb") as f:
            pickle.dump(dists, f)
    return dists

