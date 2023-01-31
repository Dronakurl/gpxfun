import base64
import calendar
import json
from pathlib import Path
import pickle
import re
import sys
import threading
from typing import Optional
from dash import Dash, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import numpy as np
import pandas as pd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn import linear_model
from sklearn.model_selection import KFold, cross_val_score
from tqdm import tqdm
from app_data_functions import get_data_from_pickle_session, parse_and_cluster
from app_layout import serve_layout
from calc_dist_matrix import calc_dist_matrix, euclidean, mae, update_dist_matrix
from cluster_it import cluster_all
from parse_gpx import update_pickle_from_folder
from plots import plotaroute, prepareplotdata, violin
from positions_from_distm import calculate_positions
from utilities import convert_bytes, getfilelist
import planar

df , mic = get_data_from_pickle_session("test")

plotaroute(df,groupfield="cluster").show()

ss=prepareplotdata( df, groupfield= "cluster")
