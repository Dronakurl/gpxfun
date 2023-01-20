import similaritymeasures
import numpy as np
import pandas as pd
from math import sqrt


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
) -> np.array:
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
