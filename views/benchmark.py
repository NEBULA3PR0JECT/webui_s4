from dash import Dash, dcc, html
import dash_bootstrap_components as dbc


class BenchmarkView(object):
    def __init__(self):
        super(BenchmarkView, self).__init__()

    def render_benchmark_content(self):
        return (dbc.Spinner(html.Div("children", id="benchmarks",style={"margin-top": "40px"}),spinner_style={"width": "6rem", "height": "6rem"}))
