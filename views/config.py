from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

class ConfigView():
    def __init__(self, *args):
        super(ConfigView, self).__init__(*args)

    def render_config_content(self):
        return html.Div([dbc.Row(
        [
            dbc.Col([dbc.Input(
                    id="input_database",
                    type="url",
                    placeholder="DB name",
                    ),
            ])
        ],
        ),
            dbc.Row(
            [
                dbc.Col([dbc.Input(
                        id="input_web_server",
                        type="url",
                        placeholder="Web Server",
                        ),
                ])
            ],
        ),
            dbc.Row(
            [
                dbc.Col([dbc.Input(
                        id="input_dataset_name",
                        type="url",
                        placeholder="Dataset",
                        ),
                ])
            ],
        ),
        ])
