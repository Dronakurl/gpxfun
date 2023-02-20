"""
All functions used to import, parse gpx files
"""
from pathlib import Path
import pickle

import gpxpy
import gpxpy.geo
import gpxpy.gpx
import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline, interp1d

from utilities import getfilelist, season_of_date
from tqdm import tqdm


def interpolateroutes(r: list) -> list:
    """interpolates and smoothes a route"""
    points = np.array([np.array(xx) for xx in r])
    _, idx = np.unique(points, axis=0, return_index=True)
    points = points[np.sort(idx)]
    distance = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1)))
    # these are some magic numbers that work best for cycle distances
    s = distance[-1] / 10000.0
    distance = np.insert(distance, 0, 0) / distance[-1]
    alpha = np.linspace(0, 1, 1000)
    # smooth the curve
    splines = [UnivariateSpline(distance, coords, s=s) for coords in points.T]
    points = np.vstack([spl(alpha) for spl in splines]).T
    # interpolate to get exactly 1000 points per curve
    distance = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1)))
    distance = np.insert(distance, 0, 0) / distance[-1]
    interpolator = interp1d(distance, points, kind="linear", axis=0)
    points = interpolator(alpha)
    points = [list(x) for x in list(points)]
    return points


def read_gpx_file(f: Path, filehandle=None) -> dict:
    """read one gpxfile"""
    p = {}
    p["dateiname"] = f.name
    if filehandle is None:
        with open(f) as fh:
            g = gpxpy.parse(fh)
    else:
        g = gpxpy.parse(filehandle)
    p["strecke"] = gpxpy.gpx.GPX.length_3d(g)
    p["datum"] = g.get_time_bounds().start_time.date()
    p["startzeit"] = g.get_time_bounds().start_time.time()
    p["monat"] = p["datum"].month
    p["wochentag"] = p["datum"].strftime("%A")
    p["jahreszeit"] = season_of_date(p["datum"])
    p["dauer"] = gpxpy.gpx.GPX.get_duration(g) / 60
    p["keywords"] = "" if g.keywords is None else g.keywords
    if f.name == "20221013T010322000.gpx":
        p["keywords"] = "heim"
    p["bergauf"] = g.get_uphill_downhill().uphill
    p["bergab"] = g.get_uphill_downhill().downhill
    x = g.get_points_data()[0]
    p["start"] = gpxpy.geo.Location(
        latitude=x.point.latitude,
        longitude=x.point.longitude,
        elevation=x.point.elevation,
    )
    x = g.get_points_data()[-1]
    p["ende"] = gpxpy.geo.Location(
        latitude=x.point.latitude,
        longitude=x.point.longitude,
        elevation=x.point.elevation,
    )
    p["luftlinie"] = p["ende"].distance_3d(p["start"])
    # p["arbeit"] = True if "arbeit" in p["keywords"].lower() else False
    # p["heim"] = True if "heim" in p["keywords"].lower() else False
    # Die Labels arbeit und heim sind unzuverlässig, also machen wir neue anhand der tatsächlichen Daten
    # start_is_arbeit = p["start"].distance_3d(arbeit) < 200
    # start_is_zuhause = (
    #     p["start"].distance_3d(kindergarten) < 100
    #     or p["start"].distance_3d(zuhause) < 100
    # )
    # ende_is_arbeit = p["ende"].distance_3d(arbeit) < 100
    # ende_is_zuhause = p["ende"].distance_3d(zuhause) < 100
    # p["arbeit"] = start_is_zuhause & ende_is_arbeit
    # p["heim"] = start_is_arbeit & ende_is_zuhause
    route = list(
        map(lambda x: [x.point.longitude, x.point.latitude], g.get_points_data())
    )
    p["route_inter"] = interpolateroutes(route)
    return p


# p=read_gpx_file(Path("data/20221013T010322000.gpx"))


def read_gpx_file_list(filelist: list, delete: bool = False) -> pd.DataFrame:
    """
    - Reads gpx files from a file list 
    - Deletes the files if delete option is set
    - Returns a result DataFrame with information for each GPX file
    """
    print(f"read_gpx_file_list: {len(filelist)} Dateien lesen")
    r = []
    for f in (pbar:=tqdm(filelist, colour="#ff00ff", desc="read GPX files")):
        pbar.set_postfix_str(f.name[0:20])
        if not str(f).endswith("gpx"):
            continue
        p = read_gpx_file(f)
        if delete:
            f.unlink()
        r.append(p)
    df = pd.DataFrame(r).convert_dtypes()
    df = df.astype(
        {
            "jahreszeit": "category",
            "wochentag": "category",
            "keywords": "category",
            "monat": "category",
        }
    )
    return df


def read_gpx_from_folder(infolder: str) -> pd.DataFrame:
    """read and parse all gpx files from a folder"""
    return read_gpx_file_list(getfilelist(infolder, suffix="gpx", withpath=True))


def update_pickle_from_list(
    filelist: list,
    mypickle: Path = Path("pickles/df.pickle"),
    delete: bool = False,
) -> tuple[pd.DataFrame, bool]:
    """update a pickle file of gpx data with a list of gpx files"""
    if not Path(mypickle).is_file():
        print(f"update_pickle_from_list: {mypickle} gibt es noch nicht")
        d = pd.DataFrame()
        fl = filelist
    else:
        with open(mypickle, "rb") as f:
            d = pickle.load(f)
        fl = [f for f in filelist if f.name not in list(d["dateiname"])]
    print(
        f"update_pickle_from_list: {len(fl)} von {len(filelist)} müssen noch eingelesen werden"
    )
    updated = len(fl) > 0
    if updated:
        d = pd.concat(
            [d, read_gpx_file_list(fl, delete=delete)], axis=0
        )
        mypickle.parents[0].mkdir(exist_ok=True)
        with open(mypickle, "wb") as f:
            pickle.dump(d, f)
    return d, updated


def update_pickle_from_folder(
    infolder: str,
    mypickle: Path = Path("pickles/df.pickle"),
    delete: bool = False,
) -> tuple[pd.DataFrame, bool]:
    """update a pickle file of gpx data with a folder containing gpx files"""
    return update_pickle_from_list(
        getfilelist(infolder, suffix="gpx", withpath=True),
        mypickle=mypickle,
        delete=delete,
    )
