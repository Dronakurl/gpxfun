"""
A script to prepare the data and test plots for gpx analysis
"""
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd
import plotly.express as px
from sklearn import linear_model
from sklearn.model_selection import KFold, cross_val_score

from calc_dist_matrix import calc_dist_matrix, euclidean, mae, update_dist_matrix
from cluster_it import cluster_all
from parse_gpx import update_pickle_from_folder
from plausi_single_route import plausi_single_route
from plots import plotaroute
from positions_from_distm import calculate_positions

# Read the gpx data from a folder. Data is stored in y pickle, so that
# it does not need to be reloaded every time.
# New files are added to the data frame with
d, updated = update_pickle_from_folder(
    infolder="/home/konrad/gpxfun/data", mypickle="pickles/df.pickle"
)

# distance matrix is generated, if not already stored in a pickle
dists = update_dist_matrix(
    d, mypickle=Path("pickles/dists.pickle"), updated=updated, simmeasure=mae
)

# Pick a random route and visualize the nearest neighbors
# plausi_single_route(d, dists, 35)

# Apply Cluster
d = cluster_all(d, dists)


print("command_line.py: exit with sys.exit. More code after this for use in a REPL mode")
sys.exit(0)

# get the names of the biggest clusters
imp_clusters = d.cluster.drop_duplicates()
imp_clusters = imp_clusters[imp_clusters.astype(bool)].sort_values()
imp_clusters = [x for x in imp_clusters if int(re.search("\D_(\d+)", x).group(1)) < 4]

# Display all routes in each cluster to see if clustering worked

fig=plotaroute(
    d[d.arbeit & d.cluster.isin(imp_clusters)],
    groupfield="cluster",
    title="Show all clusters for arbeit",
)
fig.show()

for g in list(np.unique(d.cluster[d.cluster.isin(imp_clusters)])):
    plotaroute(d[d.cluster == g], groupfield="dateiname", title=f"Cluster {g}").show()

dr = d[d.arbeit]
dr = dr[~dr.cluster.isin(imp_clusters)]
plotaroute(dr, groupfield="cluster", title=f"Kleinere Cluster").show()


# Transform in euclidean coordinates
y = pd.DataFrame(calculate_positions(dists["arbeit"]))
y["point"] = pd.Series(zip(y[0], y[1]))
y = pd.concat(
    [
        pd.DataFrame(dists["arbeit_dateinamen"], columns=["dateiname"]),
        y.drop([0, 1], axis=1),
    ],
    axis=1,
)
mydist = calc_dist_matrix(y, simmeasure=euclidean, compvar="point")

# # Matrix visualisieren
# px.imshow(dists["arbeit"])
# px.imshow(mydist)
# px.imshow(mydist - dists["arbeit"])

# Euclidean visualisieren
df = d[d.arbeit].copy()
df = df.merge(y, how="outer", on="dateiname")
df["distx"] = df.point.apply(lambda x: x[0])
df["disty"] = df.point.apply(lambda x: x[1])
px.scatter(df, x="distx", y="disty", color="cluster")

# Anzahl stops


dr = d[d.arbeit].copy()
# exclude some strange outliers
dr = dr[dr.dateiname != "20220920T075709000.gpx"]
dr.cluster = dr.cluster.apply(lambda x: x if x in imp_clusters else "sonstige")

ds=dr[["jahreszeit","wochentag","cluster","dauer"]]
ds=dr[["cluster","dauer"]]
X=ds.drop("dauer",axis=1)
X=pd.get_dummies(X)
y=ds[["dauer"]]

logr = linear_model.LinearRegression()
logr.fit(X,y)
logr.coef_
clf = linear_model.LinearRegression()
k_folds = KFold(n_splits = 5)
scores = cross_val_score(clf, X, y, cv = k_folds)
print("Cross Validation Scores: ", scores)
print("Average CV Score: ", scores.mean())
print("Number of CV Scores used in Average: ", len(scores))

