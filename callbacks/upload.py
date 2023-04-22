import base64
import logging
from pathlib import Path
import threading

from dash import Input, Output, State, callback, ctx, no_update
from tqdm import tqdm

from dash_app.app_data_functions import parse_and_cluster


log = logging.getLogger("gpxfun." + __name__)


@callback(
    Output("numberoffiles", "data"),
    Input("upload-data", "contents"),
    Input("upload-data", "filename"),
    State("sessionid", "data"),
    prevent_initial_call=True,
)
def upload(contents, filenames, sessionid):
    """upload gpx data to session folder and start parsing thread"""
    log.debug(str(ctx.triggered_id))
    if ctx.triggered_id == None:
        return no_update
    # create sessionid folder
    (Path("sessions") / sessionid).mkdir(parents=True, exist_ok=True)
    # store alle files in a tmp session directory
    for ii in tqdm(range(len(contents)), colour="#ffff00", desc="GPX -> session folder"):
        filename = filenames[ii]
        if Path(filename).suffix != ".gpx":
            log.warning(f"provided {filename}, which is not a gpx file")
            continue
        cc = contents[ii]
        _, content_string = cc.split(",")
        strdata = base64.b64decode(content_string).decode("utf-8")
        with open(Path("sessions") / sessionid / filename, "w") as f:
            f.write(strdata)
    log.debug(f"upload({sessionid}): number of files = {len(contents)}")
    mythread = threading.Thread(
        target=parse_and_cluster,
        name="read",
        kwargs={
            "infolder": Path("sessions") / sessionid,
            "mypickle": Path("sessions") / sessionid / "df.pickle",
            "delete": True,
        },
    )
    mythread.start()
    return len(contents)
