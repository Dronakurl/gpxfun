"""
All functions used to import, parse gpx files
"""
from pathlib import Path
import gpxpy, gpxpy.gpx, gpxpy.geo
import numpy as np
import pandas as pd
import pickle
from scipy.interpolate import UnivariateSpline, interp1d

from custom_locations import arbeit, kindergarten, zuhause
from utilities import getfilelist, season_of_date


def interpolieren(r: list) -> list:
    """Nimmt eine Kurve und glättet und interpoliert sie"""
    points = np.array([np.array(xx) for xx in r])
    _, idx = np.unique(points, axis=0, return_index=True)
    points = points[np.sort(idx)]
    distance = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1)))
    # Das scheint die beste Wahl für den Parameter zu sein
    s = distance[-1] / 10000.0
    distance = np.insert(distance, 0, 0) / distance[-1]
    alpha = np.linspace(0, 1, 1000)
    # rauschen wegmachen
    splines = [UnivariateSpline(distance, coords, s=s) for coords in points.T]
    points = np.vstack([spl(alpha) for spl in splines]).T
    # interpolieren
    distance = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1)))
    distance = np.insert(distance, 0, 0) / distance[-1]
    interpolator = interp1d(distance, points, kind="linear", axis=0)
    points = interpolator(alpha)
    points = [list(x) for x in list(points)]
    return points


def read_gpx_file(f: Path) -> dict:
    """read one gpxfile"""
    p = {}
    p["dateiname"] = f.name
    print(f"Auf geht's für Dateiname {f}")
    with open(f) as fh:
        g = gpxpy.parse(fh)
    p["strecke"] = gpxpy.gpx.GPX.length_3d(g)
    p["datum"] = g.get_time_bounds().start_time.date()
    p["monat"] = p["datum"].month
    p["wochentag"] = p["datum"].strftime("%A")
    p["jahreszeit"] = season_of_date(p["datum"])
    p["dauer"] = gpxpy.gpx.GPX.get_duration(g)
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
    start_is_arbeit = p["start"].distance_3d(arbeit) < 200
    start_is_zuhause = (
        p["start"].distance_3d(kindergarten) < 100
        or p["start"].distance_3d(zuhause) < 100
    )
    ende_is_arbeit = p["ende"].distance_3d(arbeit) < 100
    ende_is_zuhause = p["ende"].distance_3d(zuhause) < 100
    p["arbeit"] = start_is_zuhause & ende_is_arbeit
    p["heim"] = start_is_arbeit & ende_is_zuhause
    p["route"] = list(
        map(lambda x: [x.point.longitude, x.point.latitude], g.get_points_data())
    )
    p["route_inter"] = interpolieren(p["route"])
    return p


def read_gpx_file_list(filelist: list) -> pd.DataFrame:
    """reads gpx files from a file list"""
    r = []
    for f in filelist:
        if not str(f).endswith("gpx"):
            continue
        p = read_gpx_file(f)
        r.append(p)
    return pd.DataFrame(r)


def read_gpx_from_folder(infolder: str) -> pd.DataFrame:
    """read and parse all gpx files from a folder"""
    return read_gpx_file_list(
        [Path(infolder) / f for f in getfilelist(infolder, suffix="gpx")]
    )


def update_pickle_from_list(
    filelist: list, mypickle: str = "pickles/df.pickle"
) -> pd.DataFrame:
    """update a pickle file of gpx data with a list of gpx files"""
    if not Path(mypickle).is_file():
        return read_gpx_file_list(filelist)

    with open(mypickle, "rb") as f:
        d = pickle.load(f)
    fl = [f for f in filelist if f.name not in d["dateiname"]]
    d = pd.concat([d, read_gpx_file_list(fl)], axis=0)

    with open(mypickle, "wb") as f:
        pickle.dump(d, f)
    return d


def update_pickle_from_folder(
    infolder: str, mypickle: str = "pickles/df.pickle"
) -> pd.DataFrame:
    """update a pickle file of gpx data with a folder containing gpx files"""
    return update_pickle_from_list(
        getfilelist(infolder, suffix="gpx", withpath=True), mypickle=mypickle
    )
