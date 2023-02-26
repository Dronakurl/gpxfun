"""
Utilities that can be reused some day
"""
import datetime
import logging
from pathlib import Path

import pandas as pd

log=logging.getLogger("gpxfun."+__name__)

def getfilelist(mypath: str, suffix: str, withpath: bool = False) -> list:
    """Find all files in folders and subfolders given a specific extension"""
    p = Path(mypath).glob("**/*." + suffix)
    l = [x for x in p if x.is_file()]
    if withpath == False:
        l = [f.name for f in l]
    return l


def getdirlist(mypath: str, withpath: bool = False) -> list:
    """Find all subfolders of a folder"""
    p = Path(mypath).glob("*")
    l = [x for x in p if x.is_dir()]
    if withpath == False:
        l = [f.name for f in l]
    return l


def season_of_date(date: datetime.date) -> str:
    """Zu einem Datumg die Jahreszeit zuordnen"""
    year = date.year
    seasons = {
        "spring": pd.date_range(
            start=datetime.date(year, 3, 21), end=datetime.date(year, 6, 20)
        ),
        "summer": pd.date_range(
            start=datetime.date(year, 6, 21), end=datetime.date(year, 9, 22)
        ),
        "autumn": pd.date_range(
            start=datetime.date(year, 9, 23), end=datetime.date(year, 12, 20)
        ),
    }
    if pd.Timestamp(date) in seasons["spring"]:
        return "spring"
    if pd.Timestamp(date) in seasons["summer"]:
        return "summer"
    if pd.Timestamp(date) in seasons["autumn"]:
        return "autumn"
    else:
        return "winter"


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

