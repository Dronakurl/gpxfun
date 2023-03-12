import logging
import threading
from pathlib import Path

from dash import Input, Output, State, callback, ctx, no_update
from utilities import getfilelist, convert_bytes

from app_layout import MYCOLOR

log = logging.getLogger("gpxfun." + __name__)

@callback(
    Output("progressbar", "value"),
    Output("progressbar", "label"),
    Output("progressbar", "color"),
    Output("storedflag", "data"),
    Output("load_textarea", "value"),
    Output("progressinterval", "disabled"),
    Output("sessionid", "data"),
    Input("progressinterval", "n_intervals"),
    State("sessionid", "data"),
    Input("numberoffiles", "data"),
    Input("picksessionid", "value"),
    prevent_initial_call=True,
)
def update_progessbar(_, sessionid, numberoffiles, picksessionid):
    """update the progress bar from the number of files remaining"""
    if ctx.triggered_id == None:
        return [no_update] * 7
    elif ctx.triggered_id == "picksessionid":
        return (
            100,
            "loaded a sessionid",
            "#00FF18",
            True,
            f"files are loaded from sessionid {picksessionid}",
            True,
            picksessionid,
        )
    elif numberoffiles < 2:
        return (
            0,
            "ERROR",
            "red",
            True,
            "Upload at least 2 GPX files",
            False,
            no_update,
        )
    filelist = getfilelist(Path("sessions") / sessionid, "gpx")
    n = len(filelist)
    storedflag = n == 0
    # check if the parsing thread is finished, otherwise, remain in state "not stored"
    for thread in threading.enumerate():
        # log.debug(f"update_progessbar({sessionid}): thread.names : {thread.name}")
        if thread.name == "read" and thread.is_alive():
            storedflag = False
    percentage = (numberoffiles - n) / numberoffiles * 100
    # log.debug( f" numberoffiles={numberoffiles}, percentage={percentage}, storedflag={storedflag}")
    if storedflag:
        filesize = convert_bytes(
            (Path("sessions") / sessionid / "df.pickle").stat().st_size
        )
        textarea = f"Finished parsing {numberoffiles} GPX files\n"
        textarea += f"Session id: {sessionid}\n"
        textarea += f"Total file size: {filesize}"
    else:
        textarea = f"Remaining files to parse ({n} of {numberoffiles})\n"
        textarea += f"Session id: {sessionid}\n"
        textarea += "\n".join(filelist)
    return (
        percentage,
        f"{numberoffiles-n} of {numberoffiles}",
        MYCOLOR if storedflag == False else "#00FF54",
        no_update if storedflag == False else storedflag,
        textarea,
        storedflag,
        no_update,
    )

@callback(
    Output("progressbar", "style"),
    Output("load_textarea", "style"),
    Output("picksessionid", "style"),
    Input("togglelog", "n_clicks"),
    State("progressbar", "style"),
    State("load_textarea", "style"),
    State("picksessionid", "style"),
    prevent_initial_call=True,
)
def togglelog(_, progress, load, pick):
    """ toggle visibility of loading items """
    if ctx.triggered_id == None:
        return [no_update] * 3
    for elmt in (progress, load, pick):
        elmt["display"]="none" if elmt.get("display","block")=="block" else "block"
    return progress, load, pick
