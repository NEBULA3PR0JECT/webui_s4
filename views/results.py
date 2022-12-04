from dash import Dash, dcc, html, ctx, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import glob


class ResultsView():
    def __init__(self, db):
        super(ResultsView, self).__init__()
        self.db = db

    def render_results_content(self, pipelines_ok, movies_table, mdfs_data):
        return html.Div([
            dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(pipelines_ok, id='pipelines-dropdown',),
                        dbc.Button('Refresh movies', id='refresh_movies',
                                n_clicks=0, style={"margin-top": "5px"}),
                        dbc.Button('Refresh jobs', id='refresh_jobs',
                                n_clicks=0, style={"margin-top": "5px"})
                    ], style={"margin-left": "5px", "margin-right": "50%", "margin-bottom": "20px"})
            ],
            ),
            # dbc.Row(
            # [
            #     dbc.Col(movies_table)
            # ],
            # ),
            dbc.Row(
                [
                    dbc.Col([movies_table]),
                    dbc.Col(id='res_preview_layout',
                            children="")  # , style={"margin-right": "25%", "margin-left": "25%"})
                ]
            ),
            dbc.Row(
                [dbc.Button('View results', id='view_results', n_clicks=0)], style={"margin-top": "5px", "margin-right": "85%", "margin-left": "5px"}),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("View MDFS"), close_button=True
                    ),
                    dbc.ModalBody(
                        mdfs_data, id="mdfs_slider"
                    ),
                    dbc.ModalFooter([""]),
                ],
                is_open=False,
                id="view_mdf",
                size="xl",
            )
        ])