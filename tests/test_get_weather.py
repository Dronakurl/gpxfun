import datetime

from gpxpy.geo import Location
import pandas as pd
import pytz

from gpxfun.get_weather import get_weather, get_weather_dict


def test_get_weather_dict():
    d = get_weather_dict(
        datetime.datetime(2022, 2, 3, 9, 0, 0, tzinfo=pytz.timezone("Europe/Berlin")),
        50,
        8,
        100,
    )
    assert d["temp"] == 7.4
    assert d["rhum"] == 90.0
    assert d["prcp"] == 0.0
    assert d["snow"] == 0.0
    assert d["wdir"] == 260.0
    assert d["wspd"] == 2.5
    assert d["wpgt"] == 7.0
    assert d["pres"] == 1020.5
    assert d["tsun"] == 0.0


def test_get_weather():
    sd = pd.DataFrame(
        {
            "startdatetime": [
                datetime.datetime(2022, 2, 3, 9, 0, 0, tzinfo=pytz.timezone("Europe/Berlin")),
                datetime.datetime(2022, 2, 3, 9, 0, 0, tzinfo=pytz.timezone("Europe/Berlin")),
            ],
            "start": [
                Location(50, 8, 100),
                Location(50, 8, 100),
            ],
        }
    )
    wd = get_weather(sd)
    assert wd.shape[0] == 2
    assert wd.shape[1] == 14
    assert wd.iloc[0]["startdatetime"] == wd.iloc[1]["startdatetime"]
    assert wd.iloc[0]["time"] == wd.iloc[1]["time"]
    assert wd.iloc[0]["temp"] == wd.iloc[1]["temp"]
    assert wd.iloc[0]["rhum"] == wd.iloc[1]["rhum"]
    assert wd.iloc[0]["prcp"] == wd.iloc[1]["prcp"]
    assert wd.iloc[0]["snow"] == wd.iloc[1]["snow"]
    assert wd.iloc[0]["wdir"] == wd.iloc[1]["wdir"]
    assert wd.iloc[0]["wspd"] == wd.iloc[1]["wspd"]
    assert wd.iloc[0]["wpgt"] == wd.iloc[1]["wpgt"]
    assert wd.iloc[0]["pres"] == wd.iloc[1]["pres"]
    assert wd.iloc[0]["tsun"] == wd.iloc[1]["tsun"]


def test_get_weather_smoke():
    get_weather_dict(
        datetime.datetime(2022, 2, 3, 9, 0, 0, tzinfo=pytz.timezone("Europe/Berlin")),
        50,
        8,
        100,
    )
