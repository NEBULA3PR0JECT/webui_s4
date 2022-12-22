from dash import Dash, dcc, html, ctx, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import glob


class ResultsView():
    def __init__(self, db):
        super(ResultsView, self).__init__()
        self.db = db

    def render_results_content(self, pipelines_ok, movies_table, mdfs_data, gt_graph_data, graph_data, gt_data, gn_data):
        return html.Div([
            dbc.Row(
                [
                    dbc.Col(dbc.Spinner([movies_table],spinner_style={"width": "6rem", "height": "6rem"})),
                    dbc.Col(id='res_preview_layout',
                            children="")  # , style={"margin-right": "25%", "margin-left": "25%"})
                ]
            ),
            dbc.Row(
                dbc.ButtonGroup(children=[dbc.Button('View results', id='view_results', n_clicks=0),
                dbc.Button('Refresh table', id='refresh_table', n_clicks=0)]),
                style={"margin-top": "5px","margin-left": "0%", "margin-right": "80%"}),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("MDFS"), close_button=True
                    ),
                    dbc.ModalBody(
                        mdfs_data, id="mdfs_slider"
                    ),
                    dbc.ModalFooter([""]),
                ],
                is_open=False,
                id="view_mdf",
                size="xl",
            ),
            graph_data,
            gt_graph_data,
            gt_data,
            gn_data
        ])