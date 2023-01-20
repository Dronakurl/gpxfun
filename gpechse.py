import os
import pickle

import numpy as np
import pandas as pd
import plotly.express as px

from calc_dist_matrix import area_comp, calc_dist_matrix, euclidean, mae
from cluster_it import cluster_it
from plausi_single_route import plausi_single_route
from plots import plotaroute
from positions_from_distm import calculate_positions
from read_gpx_from_folder import update_pickle_from_folder


update_pickle_from_folder(infolder="~/gpxfun/data", mypickle="pickles/df.pickle")

# Abstandsmatrix ausrechen
if os.path.exists("pickles/dists.pickle"):
    with open("pickles/dists.pickle", "rb") as f:
        dists = pickle.load(f)
else:
    dists = {}
    for a in ["arbeit", "heim"]:
        print(f"Berechne die Abstandsmatrix für {a}")
        dsub = d[d[a]]
        dists[a + "_dateinamen"] = list(dsub.loc[:, "dateiname"])
        dists[a] = calc_dist_matrix(dsub, simmeasure=mae)
    with open("pickles/dists.pickle", "wb") as f:
        pickle.dump(dists, f)

# Für eine einzige Route die "nächsten Nachbarn plausibilisieren"
plausi_single_route(d, dists, 35)

# Cluster bilden
d["cluster"] = ""
d.index = d.dateiname
for a in ["arbeit", "heim"]:
    dfcluster = cluster_it(
        dists[a], dists[a + "_dateinamen"], clusterlabel=a, min_cluster_size=3
    )
    d.update(dfcluster, join="left")
d = d.reset_index(drop=True)
print(d.groupby("cluster").size())
with open("pickles/df.pickle", "wb") as f:
    pickle.dump(d, f)

# Cluster plausibilisieren
# # jeden cluster mal anzeigen, ob die irgendwas gemein haben
for g in list(np.unique(d.cluster[d.cluster != ""])):
    plotaroute(d[d.cluster == g], groupfield="dateiname")
# Cluster zeigen, -1 sind die Ausreißer
plotaroute(d[d.arbeit & ~d.cluster.str.endswith("-1")], groupfield="cluster")
# plotaroute(d[d.arbeit & d.cluster.str.endswith("-1")], groupfield="dateiname")

# In euclidean Koordination transformieren
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

# Matrix visualisieren
px.imshow(dists["arbeit"])
px.imshow(mydist)
px.imshow(mydist - dists["arbeit"])

# Euclidean visualisieren
df = d[d.arbeit].copy()
df.merge(y, how="outer", on="dateiname")
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
