"""
A script to prepare the data and test plots for gpx analysis
"""
import pickle
import re
import numpy as np
import pandas as pd
import plotly.express as px
from calc_dist_matrix import calc_dist_matrix, euclidean, mae, update_dist_matrix
from cluster_it import cluster_all
from plausi_single_route import plausi_single_route
from plots import plotaroute
from positions_from_distm import calculate_positions
from read_gpx_from_folder import update_pickle_from_folder

# Read the gpx data from a folder. Data is stored in y pickle, so that
# it does not need to be reloaded every time.
# New files are added to the data frame with
d, updated = update_pickle_from_folder(
    infolder="/home/konrad/gpxfun/data", mypickle="pickles/df.pickle"
)

# distance matrix is generated, if not already stored in a pickle
dists = update_dist_matrix(
    d, mypickle="pickles/dists.pickle", updated=updated, simmeasure=mae
)

# Pick a random route and visualize the nearest neighbors
# plausi_single_route(d, dists, 35)

# Apply Cluster
d = cluster_all(d, dists)

# get the names of the biggest clusters
imp_clusters = d.cluster.drop_duplicates()
imp_clusters = imp_clusters[imp_clusters.astype(bool)].sort_values()
imp_clusters = [x for x in imp_clusters if int(re.search("\D_(\d+)", x).group(1)) < 4]

# Display all routes in each cluster to see if clustering worked

plotaroute(
    d[d.arbeit & d.cluster.isin(imp_clusters)],
    groupfield="cluster",
    title="Show all clusters for arbeit",
).show()

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

# Dashboard mit den Ergebnissen, 3 größte Cluster
# Präsentation für den Hackaton
# Anzahl stops

# # mittlere Zeit je Jahreszeit
# fig=px.histogram(d[d.arbeit],x="dauer",y="jahreszeit",orientation="h",histnorm="probability",
#     labels={"jahreszeit":"Jahreszeit","y":"Anteil"})
# fig.update_layout(
#     bargap=.2,
#     xaxis_title="Dauer",
#     # yaxis = dict(
#         # tickmode = 'array',
#         # tickvals = [0,1,2,3,4,5,6],
#         # ticktext = ["Mo","Di","Mi","Do","Fr","Sa","So"]
#     # )
# )
# fig.show()
