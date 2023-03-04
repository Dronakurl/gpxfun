import datetime

import meteostat
import pandas as pd
import pytz
import logging
from tqdm import tqdm

log = logging.getLogger("gpxfun." + __name__)


def get_weather(
    d: pd.DataFrame, dt_col: str = "startdatetime", loc_col: str = "start"
) -> pd.DataFrame:
    """
    Get weather data from meteostat and attach it to the DataFrame
    :param d: pandas DataFrame with date and location data
    :type d: pandas.DataFrame
    :param dt_col: column name of d containing the datetime data
            the datetime must contain the timezone
    :type dt_col: str
    :param loc_col: column name of d containing the location data. Elements in
            this column most have longitude and latitude and elevation attributes
    """
    awd = pd.DataFrame()
    for index, row in (
        pbar := tqdm(
            d.iterrows(),
            colour="#ffcc44",
            desc="get weather",
            total=d.shape[0],
        )
    ):  # pyright: ignore
        pbar.set_postfix_str(row[dt_col])  # pyright: ignore
        dt = row[dt_col].replace(tzinfo=None)  # pyright: ignore
        wd = meteostat.Hourly(
            meteostat.Point(
                row[loc_col].latitude,
                row[loc_col].longitude,
                row[loc_col].elevation,  # pyright: ignore
            ),
            dt,
            dt + datetime.timedelta(hours=1),
            row[dt_col].tzinfo.zone,  # pyright: ignore
        ).fetch()
        wd = wd.head(1).reset_index().rename(index={0: index})
        awd = pd.concat([awd, wd])
    return pd.merge(d, awd, how="left", left_index=True, right_index=True)


def get_weather_dict(dt: datetime.datetime, lat: float, lon: float, ele: float) -> dict:
    """
    gets the weather data from meteostat for a datetime and a latitude
    """
    log.debug(f"dt={dt}, lat={lat}, lon={lon}, ele={ele}")
    if dt.tzinfo == None:
        timez = "Europe/Berlin"
        log.warning(
            f"No timezone included in datetime variable {dt}, defaulting to CET"
        )
    else:
        timez = str(dt.tzinfo)
    dt_dummy = dt.replace(tzinfo=None)
    wd = meteostat.Hourly(
        meteostat.Point(lat, lon, int(ele)),
        dt_dummy,
        dt_dummy + datetime.timedelta(hours=1, minutes=1),
        timez,
    ).fetch()
    d = dict()
    if len(wd) > 0:
        d = wd.iloc[0].to_dict()
    else:
        log.warning(f"could not find weather data")
    return d


if __name__ == "__main__":
    from mylog import get_log
    log = get_log()
    print(
        get_weather_dict(
            datetime.datetime(
                2022, 2, 3, 9, 0, 0, tzinfo=pytz.timezone("Europe/Berlin")
            ),
            50,
            8,
            100,
        )
    )
