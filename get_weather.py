import meteostat
from tqdm import tqdm
import pandas as pd
import datetime


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
    ):
        pbar.set_postfix_str(row[dt_col])
        dt = row[dt_col].replace(tzinfo=None)
        wd = meteostat.Hourly(
            meteostat.Point(
                row[loc_col].latitude, row[loc_col].longitude, row[loc_col].elevation
            ),
            dt,
            dt + datetime.timedelta(hours=1),
            row[dt_col].tzinfo.zone,
        ).fetch()
        wd = wd.head(1).reset_index().rename(index={0: index})
        awd = pd.concat([awd, wd])
    return pd.merge(d, awd, how="left", left_index=True, right_index=True)
