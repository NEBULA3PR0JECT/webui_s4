from dash import Dash, dcc, html
import dash_bootstrap_components as dbc


class JobsView(object):
    def __init__(self):
        super(JobsView, self).__init__()

    def render_jobs_content(self):
        return(dbc.Spinner(html.Div("Loading", id="gradient-jobs"),spinner_style={"width": "6rem", "height": "6rem"}))
