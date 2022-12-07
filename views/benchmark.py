from dash import Dash, dcc, html



class BenchmarkView(object):
    def __init__(self):
        super(BenchmarkView, self).__init__()

    def render_benchmark_content(self):
        return html.Div("children", id="benchmarks")
