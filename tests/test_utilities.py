from utils.utilities import safe_int_list_cast
from utils.utilities import getfilelist
from utils.utilities import season_of_date
import datetime


def test_safe_int_list_cast():
    """For each item of the passed list:
    Cast an object to str and if it is a number, it will be casted to int,
    returns the original object, if not
    """
    assert safe_int_list_cast([]) == []
    assert safe_int_list_cast([1]) == [1]
    assert safe_int_list_cast([1, 2]) == [1, 2]
    assert safe_int_list_cast([1, 2, 3]) == [1, 2, 3]
    assert safe_int_list_cast([1, 2, "3"]) == [1, 2, 3]
    assert safe_int_list_cast([1, 2, "3", "a"]) == [1, 2, 3, "a"]
    assert safe_int_list_cast([1, 2, "3", "a", 4.5]) == [1, 2, 3, "a", 4.5]
    assert safe_int_list_cast([1, 2, "3", "a", 4.5]) == [1, 2, 3, "a", 4.5]


def test_getfilelist(tmp_path):
    tmp_path.joinpath("test1.gpx").touch()
    tmp_path.joinpath("test2.gpx").touch()
    tmp_path.joinpath("test2.txt").touch()
    assert sorted(getfilelist(tmp_path, "gpx")) == ["test1.gpx", "test2.gpx"]
    assert sorted(getfilelist(tmp_path, "gpx", withpath=True)) == [
        tmp_path / "test1.gpx",
        tmp_path / "test2.gpx",
    ]


def test_season_of_date():
    """Get a season from a date"""
    assert season_of_date(datetime.date(2020, 3, 21)) == "spring"
    assert season_of_date(datetime.date(2020, 6, 21)) == "summer"
    assert season_of_date(datetime.date(2020, 9, 23)) == "autumn"
    assert season_of_date(datetime.date(2020, 12, 21)) == "winter"
