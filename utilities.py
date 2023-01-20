'''
Utilities that can be reused some day
'''
import datetime
from pathlib import Path

import pandas as pd


def getfilelist(mypath: str, suffix: str, withpath: bool = False) -> list:
    """Finde in einem Ordner alle Dateien mit einer bestimmten Endung"""
    p = Path(mypath).glob('**/*.'+suffix)
    l = [x for x in p if x.is_file()]
    if withpath==False:
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
