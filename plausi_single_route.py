import pandas as pd
import numpy as np
from plots import plotaroute

def plausi_single_route(d: pd.DataFrame, dists: np.array, nn:int):
    # Abstände dranmergen 
    df = d.copy()
    for a in ["arbeit", "heim"]:
        dists_df = pd.concat(
            [
                pd.DataFrame(dists[a + "_dateinamen"], columns=["dateiname"]),
                pd.DataFrame(
                    dists[a], columns=["dist_"+a+"_" + f for f in dists[a + "_dateinamen"]]
                ),
            ],
            axis=1,
        )
        df = df.merge(dists_df, how="left", on="dateiname")

    # Maß plausibilisieren: Für irgendeine Kurve die 4 nächsten Kurven raussuchen
    samp = df.loc[df.arbeit].iloc[nn]
    dn = samp.dateiname
    samp = (
        # samp[[x for x in samp.keys() if type(x) == int]]
        samp.loc[[x for x in samp.keys() if x.startswith("dist_arbeit")]]
        .sort_values()
        .head(4)
        .index.to_list()
    )
    samp = [dn.split("_")[-1] for dn in samp ]
    print(df.loc[df.dateiname.isin(samp)].loc[:, ["dateiname", "dist_arbeit_"+dn]])
    plotaroute(df.loc[df.dateiname.isin(samp)], groupfield="dateiname")

