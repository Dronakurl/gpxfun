
from gpxfun.parse_gpx import read_gpx_from_folder
from gpxfun.calc_dist_matrix import calc_dist_matrix

def test_calc_dist_matrix():
    """
    Test the distance matrix calculation
    """
    df = read_gpx_from_folder("tests/data")
    dist = calc_dist_matrix(df, simmeasure="mae")

