from callbacks import choose_analyzer
# from dash.html import Div
# from dash.dcc import Checklist, Input

def test_choose_analyzer():
    inp, sty = choose_analyzer("AnalyzeLasso", [{"display": "none"}, {"display": "none"}], [{"analyzerid": "AnalyzeLasso"}, {"analyzerid": "AnalyzeLassoCV"}])
    assert str(inp)=="Div([Checklist(options={'season': 'Season', 'weekday': 'Weekday', 'cluster': 'Route cluster', 'startendcluster': 'Start/end cluster', 'starttime': 'Start time', 'temp': 'Temperature'}, value=['season', 'weekday', 'cluster', 'startendcluster', 'starttime', 'temp'], inputStyle={'display': 'inline', 'padding-right': '20px'}, labelStyle={'display': 'block'}, id={'component': 'analyzerinputs', 'analyzerid': 'AnalyzeLasso', 'id': 'vars'}), Input(id={'component': 'analyzerinputs', 'analyzerid': 'AnalyzeLasso', 'id': 'alpha'}, max=1, min=0, step=0.1, type='number', value=0.1)])"
    assert sty==[{'display': 'block'}, {'display': 'none'}]


