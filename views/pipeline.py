from dash import Dash, dcc, html, ctx, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import glob

local_files = []
for i in glob.glob("/datasets/msrvtt/*"):
    #print(local_files)
    local_files.append({"fname": i, "path": "msrvtt"})
local_files_hw = []
for i in glob.glob("//datasets/hollywood2/Hollywood2/AVIClips/*"):
    #print(local_files)
    local_files_hw.append({"fname": i, "path": "hw2"})

table_header = [
    html.Thead(html.Tr([html.Th("File"), html.Th("URL"), html.Th("Source")]))
]

class PipelineView():
    def __init__(self, db):
        super(PipelineView, self).__init__()
        self.db = db

    def render_pipeline_content(self):
        return html.Div([
        #dbc.Navbar(dark = True, color="dark",children=[html.H3('NEBULA3 Pipeline')]),
        #dbc.Row(dbc.Col(html.H1(style={"margin-left": "30%", "margin-top": "25px"},children=''))),
        dbc.Row(
            [
                #dbc.Col(),
                dbc.Col(
                    [dbc.Input(
                        id="input_url",
                        type="url",
                        placeholder="ENTER VIDEO/IMAGE URL",
                    ),
                        #dbc.Switch(label=video_or_image_lable, id='v_or_i', style={"margin-left": "5px"}),
                        #html.P(id="standalone-radio-check-output"),
                    ]),
                dbc.Col(dbc.ButtonGroup(children=[
                        dbc.Button('Preview Video/Image', id='url_p', n_clicks=0)
                        #dbc.Button('Add to batch', id='url_d', n_clicks=0, style={"margin-left": "5px"})
                        # dbc.Button('Clean Batch', id='url_clean', n_clicks=0, style={"margin-left": "5px"}),
                        # dbc.Button('Browse Files', id='url_modal', n_clicks=0, style={"margin-left": "5px"}),
                        # dbc.Button('Start Pipeline', id='url_s', n_clicks=0, style={"margin-left": "5px"})
                        ]))
                #dbc.Col()
            ],
            style={"margin-top": "25px", "margin-left": "0%"}
        ),
        dbc.Row(
            [
                dbc.Col(id='preview_layout',
                        children="")
            ],
            style={"margin-left": "0%", "margin-right": "40%", "margin-top": "20px"}
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.ButtonGroup(children=[
                            dbc.Button('Add to batch', id='url_d', n_clicks=0),
                            dbc.Button('Clean Batch', id='url_clean',
                                    n_clicks=0, style={"margin-left": "5px"}),
                            #dbc.Button('Browse Files', id='url_browse', n_clicks=0, style={"margin-left": "5px"}),
                            dbc.Button('Start Pipeline', id='url_s',
                                    n_clicks=0, style={"margin-left": "20px"}),
                            dbc.Button('Jobs status', id='url_mon',
                                    n_clicks=0, style={"margin-left": "5px"})
                        ]),
                        dbc.ButtonGroup(children=[
                            dbc.Button('Browse MSRVTT', id='url_browse',
                                    n_clicks=0, style={"margin-left": "20px"}),
                            dbc.Button('Browse HW2', id='url_browse_h',
                                    n_clicks=0, style={"margin-left": "5px"})
                        ])
                    ]
                )
            ],
            style={"margin-top": "25px", "margin-left": "0%"}
        ),
        dbc.Row(
            [
                dbc.Col(id='main_layout',
                        children=dbc.Table(table_header, bordered=False, dark=True, id='url_table'))
            ], style={"margin-left": "0%", "margin-right": "22%", "margin-top": "20px"}
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(
                    "Local Dataset MSRVTT, selected files will be added to batch")),
                dbc.ModalBody(children=dash_table.DataTable(id='files_table',
                                                            columns=[
                                                                {"name": "File name", "id": "fname"}, {
                                                                    "name": "Dataset", "id": "path"}
                                                            ],
                                                            style_header={
                                                                'backgroundColor': 'rgb(30, 30, 30)',
                                                                'color': 'dark'
                                                            },
                                                            style_data={
                                                                'backgroundColor': 'rgb(30, 30, 30)',
                                                                'color': 'dark'
                                                            },
                                                            data=local_files,
                                                            editable=True,
                                                            #filter_action="native",
                                                            sort_action="native",
                                                            sort_mode="multi",
                                                            column_selectable="single",
                                                            row_selectable="multi",
                                                            row_deletable=True,
                                                            selected_columns=[],
                                                            selected_rows=[],
                                                            page_action="native",
                                                            page_current=0,
                                                            page_size=30,
                                                            )),
            ],
            id="modal-xl",
            size="xl",
            is_open=False,
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(
                    "Local HW2 Dataset, selected files will be added to batch")),
                dbc.ModalBody(children=dash_table.DataTable(id='files_table_hw',
                                                            columns=[
                                                                {"name": "File name", "id": "fname"}, {
                                                                    "name": "Dataset", "id": "path"}
                                                            ],
                                                            style_header={
                                                                'backgroundColor': 'rgb(30, 30, 30)',
                                                                'color': 'dark'
                                                            },
                                                            style_data={
                                                                'backgroundColor': 'rgb(30, 30, 30)',
                                                                'color': 'dark'
                                                            },
                                                            data=local_files_hw,
                                                            editable=True,
                                                            #filter_action="native",
                                                            sort_action="native",
                                                            sort_mode="multi",
                                                            column_selectable="single",
                                                            row_selectable="multi",
                                                            row_deletable=True,
                                                            selected_columns=[],
                                                            selected_rows=[],
                                                            page_action="native",
                                                            page_current=0,
                                                            page_size=30,
                                                            )),
            ],
            id="modal-xl-hw",
            size="xl",
            is_open=False,
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle("Start Status"), close_button=True
                ),
                dbc.ModalBody(
                    "Job status: ", id="status"
                ),
                dbc.ModalFooter(),
            ],
            id="modal-dismiss",
            #is_open=False,
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle("Job Status"), close_button=True
                ),
                dbc.ModalBody(
                    "Job status: ", id="job_status"
                ),
                dbc.ModalFooter(dbc.Button(
                    'All successed jobs', id='all_jobs', n_clicks=0, style={"margin-left": "5px"})),
            ],
            id="modal-job-status",
            size="xl",
            #is_open=False,
        ),
        dcc.Store(id='intermediate-value')
        ])