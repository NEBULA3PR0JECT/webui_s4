from dash import Dash, dcc, html



class JobsView(object):
    def __init__(self):
        super(JobsView, self).__init__()

    def render_jobs_content(self):
        return html.Div("Loading", id="gradient-jobs")
