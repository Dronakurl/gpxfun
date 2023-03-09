import logging

from dash import Input, Output, callback, ctx, html, ALL, State
from analyzer_factory import AnalyzerFactory


log = logging.getLogger("gpxfun." + __name__)


@callback(
    Output("analyzerresultscard", "children"),
    Output("analyzer_dropdown", "options"),
    Output("analyzer_dropdown", "value"),
    Input("sessionid", "data"),
    prevent_initial_call=False,
)
def update_analyzer_dropdown(_):
    """Initialize the dropdown and results panels for the analyzer section """
    log.debug(str(ctx.triggered_id))
    af = AnalyzerFactory.avail_analyzers
    log.debug(f"Available analyzers: {' '.join(af)}")
    divs = []
    for a in af:
        divs.append(
            html.Div(
                f"no results yet",
                style={"display": "none"},
                id={"component": "analyzerresult", "analyzerid": a},
            )
        )
    return divs, af, af[0]


@callback(
    Output("analyzeroptionscard", "children"),
    Output({"component": "analyzerresult", "analyzerid": ALL}, "style"),
    Input("analyzer_dropdown", "value"),
    State({"component": "analyzerresult", "analyzerid": ALL}, "style"),
    State({"component": "analyzerresult", "analyzerid": ALL}, "id"),
    prevent_initial_call=True,
)
def choose_analyzer(analyzerid, styles, ids):
    log.debug(str(ctx.triggered_id))
    log.debug(str(styles))
    log.debug(str(ids))
    log.debug(f"analyzerid = {str(analyzerid)}")
    returnstyles=styles
    assert len(returnstyles)==len(ids)
    for i in range(len(returnstyles)):
        if ids[i].get("analyzerid") == analyzerid:
            returnstyles[i]={"display":"block"}
        else:
            returnstyles[i]={"display":"none"}
    return AnalyzerFactory().get_dash_inputs(analyzerid), returnstyles
