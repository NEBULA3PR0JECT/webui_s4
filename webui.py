from ast import increment_lineno
from dash import Dash, dcc, html, ctx, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import json
from pytube import YouTube
import glob
import base64
import requests
from gradient import WorkflowsClient
import yaml
import uuid
from arango import ArangoClient
import dash_cytoscape as cyto
from views.config import ConfigView
from views.pipeline import PipelineView
from views.results import ResultsView
from views.jobs import JobsView

arango_host = "http://172.83.9.249:8529"
w_server = 'http://74.82.29.209:9000/msrvtt/'
hw2_w_server = 'http://74.82.29.209:9000/datasets/hollywood2/Hollywood2/AVIClips/'
web_server_prefix = 'http://74.82.29.209:9000/'
movie_id = ""

j_status = []
j_status.append("")
app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
# replace with your own image
image_filename = 'marvel-nebula-png-picture-stock-nebula-guardians-of-the-galaxy-cartoo-11562973029avtizra9bu.png'
#encoded_image = base64.b64encode(open(image_filename, 'rb').read())
#print(encoded_image)
local_files = []
for i in glob.glob("/datasets/msrvtt/*"):
    #print(local_files)
    local_files.append({"fname": i, "path": "msrvtt"})
local_files_hw = []
for i in glob.glob("//datasets/hollywood2/Hollywood2/AVIClips/*"):
    #print(local_files)
    local_files_hw.append({"fname": i, "path": "hw2"})
video_or_image_lable = "Image/Video"
video_or_image = []
video_or_image.append('video')
batch_url_list = []
batch_name_list = []
movies = ""
wf_template = {
    "movies": {},
    "tasks": {},
    "inputs": {
        "videoprocessing": {
            "is_async": 'true',
            "movies": movies,
            "output": "db",
            "overwrite": 'true',
            "save_movies": 'true'
        }
    }
}

client = ArangoClient(hosts=arango_host)
db = client.db("prodemo", username='nebula', password='nebula')

# create view components
config_view = ConfigView()
pipeline_view = PipelineView(db)
results_view = ResultsView(db)
jobs_view = JobsView()

def start_job_rest():
    movies = []
    headers = {'Content-type': 'application/json'}
    for movie in batch_url_list:
        _movie = {"movie_id": "", "url": movie, "type": "file"}
        movies.append(_movie)
    payload = {"movies": movies,
               "save_movies": 'true',  # if you want to save movies/frames on disk
               "output": "db",
               "is_async": 'true',
               "overwrite": 'true'  # to overwrite existing results - re-run
               }
    print(payload)
    response = requests.post(
        'http://74.82.28.218:48005/process/movies', json=payload, headers=headers)
    return response.json()


def start_job():
    movies = []
    gradient_key = '5d88bfa5909b30076829c101624d67'
    workflow_client = WorkflowsClient(gradient_key)

    for movie in batch_url_list:
        if movie.split('.')[-1] == 'mp4' or movie.split('.')[-1] == 'avi':
            _movie = {"movie_id": "", "url": movie, "type": "video"}
        else:
            _movie = {"movie_id": "", "url": movie, "type": "movie"}
        movies.append(_movie)
    pipeline_entry = wf_template
    pipeline_entry['inputs']['videoprocessing']['movies'] = movies

    pipeline_entry['id'] = str(uuid.uuid4())
    pipeline_entry['_key'] = pipeline_entry['id']
    db.collection("pipelines").insert(pipeline_entry)
    spec_path_in = "./" + pipeline_entry['id'] + "_workflow-spec.yaml"
    URL = "https://raw.githubusercontent.com/NEBULA3PR0JECT/nebula3_pipeline/main/sprint4.yaml"
    response = requests.get(URL)
    content = response.text.replace(
        "PIPELINE_ID: \"123456789\"", "PIPELINE_ID: " + "\"" + pipeline_entry['id'] + "\"")
    #print(content)
    f = open(spec_path_in, "w")
    f.write(content)
    f.close()
    # spec_path = "./workflow-spec.yaml"
    yaml_spec = open(spec_path_in, 'r')
    spec = yaml.safe_load(yaml_spec)

    #print(pipeline_entry)
    intermediate_value = workflow_client.run_workflow(
        workflow_id='cdc9127e-6c61-43b2-95fc-ba3ea1708950',
        spec=spec,
        inputs=None
    )
    intermediate_value['pipeline_id'] = pipeline_entry['id']
    return(intermediate_value)


def get_pipelines():
    pipelines_ok = []
    pipelines_failed = []
    pipelines = []
    for pl in db.collection("pipelines").all():
        if 'videoprocessing' in pl['tasks']:
            if pl['tasks']['videoprocessing'] == 'success':
                pipelines_ok.append(pl['_key'])
            else:
                pipelines_failed.append(pl['_key'])
            pipelines.append(pl)
    return(pipelines_ok, pipelines_failed)


def get_movies():
    movies = []
    results = []
    movie_idx = []
    results_idx = []
    for res in db.collection("s4_llm_output").all():
        results.append(res)
        results_idx.append(res['movie_id'])
    for movie in db.collection("Movies").all():
        print(movie)
        if movie['_id'] in results_idx:
            if 'name' in movie and 'url_path' in movie:
                movies.append({'path': movie['url_path'], 'id': movie['_id']})
        else:
            print('Not found in res: ', movie['_id'])
    return(movies[::-1], results)

def get_mdfs(movie_id):
    mdfs = []
    for res in db.collection("s4_llm_output").find({'movie_id': movie_id}):
        mdfs.append(res)
    return(mdfs)


all_movies, all_results = get_movies()
pipelines_ok, pipelines_failed = get_pipelines()

table_header = [
    html.Thead(html.Tr([html.Th("File"), html.Th("URL"), html.Th("Source")]))
]
st_layout = dbc.Table(table_header, bordered=False, dark=True, id='url_table')

# pipeline_layout = [
#     #dbc.Navbar(dark = True, color="dark",children=[html.H3('NEBULA3 Pipeline')]),
#     #dbc.Row(dbc.Col(html.H1(style={"margin-left": "30%", "margin-top": "25px"},children=''))),
#     dbc.Row(
#         [
#             #dbc.Col(),
#             dbc.Col(
#                 [dbc.Input(
#                     id="input_url",
#                     type="url",
#                     placeholder="ENTER VIDEO/IMAGE URL",
#                 ),
#                     #dbc.Switch(label=video_or_image_lable, id='v_or_i', style={"margin-left": "5px"}),
#                     #html.P(id="standalone-radio-check-output"),
#                 ]),
#             dbc.Col(dbc.ButtonGroup(children=[
#                     dbc.Button('Preview Video/Image', id='url_p', n_clicks=0)
#                     #dbc.Button('Add to batch', id='url_d', n_clicks=0, style={"margin-left": "5px"})
#                     # dbc.Button('Clean Batch', id='url_clean', n_clicks=0, style={"margin-left": "5px"}),
#                     # dbc.Button('Browse Files', id='url_modal', n_clicks=0, style={"margin-left": "5px"}),
#                     # dbc.Button('Start Pipeline', id='url_s', n_clicks=0, style={"margin-left": "5px"})
#                     ]))
#             #dbc.Col()
#         ],
#         style={"margin-top": "25px", "margin-left": "0%"}
#     ),
#     dbc.Row(
#         [
#             dbc.Col(id='preview_layout',
#                     children="")
#         ],
#         style={"margin-left": "0%", "margin-right": "40%", "margin-top": "20px"}
#     ),
#     dbc.Row(
#         [
#             dbc.Col(
#                 [
#                     dbc.ButtonGroup(children=[
#                         dbc.Button('Add to batch', id='url_d', n_clicks=0),
#                         dbc.Button('Clean Batch', id='url_clean',
#                                    n_clicks=0, style={"margin-left": "5px"}),
#                         #dbc.Button('Browse Files', id='url_browse', n_clicks=0, style={"margin-left": "5px"}),
#                         dbc.Button('Start Pipeline', id='url_s',
#                                    n_clicks=0, style={"margin-left": "20px"}),
#                         dbc.Button('Jobs status', id='url_mon',
#                                    n_clicks=0, style={"margin-left": "5px"})
#                     ]),
#                     dbc.ButtonGroup(children=[
#                         dbc.Button('Browse MSRVTT', id='url_browse',
#                                    n_clicks=0, style={"margin-left": "20px"}),
#                         dbc.Button('Browse HW2', id='url_browse_h',
#                                    n_clicks=0, style={"margin-left": "5px"})
#                     ])
#                 ]
#             )
#         ],
#         style={"margin-top": "25px", "margin-left": "0%"}
#     ),
#     dbc.Row(
#         [
#             dbc.Col(id='main_layout',
#                     children=dbc.Table(table_header, bordered=False, dark=True, id='url_table'))
#         ], style={"margin-left": "0%", "margin-right": "22%", "margin-top": "20px"}
#     ),
#     dbc.Modal(
#         [
#             dbc.ModalHeader(dbc.ModalTitle(
#                 "Local Dataset MSRVTT, selected files will be added to batch")),
#             dbc.ModalBody(children=dash_table.DataTable(id='files_table',
#                                                         columns=[
#                                                             {"name": "File name", "id": "fname"}, {
#                                                                 "name": "Dataset", "id": "path"}
#                                                         ],
#                                                         style_header={
#                                                             'backgroundColor': 'rgb(30, 30, 30)',
#                                                             'color': 'dark'
#                                                         },
#                                                         style_data={
#                                                             'backgroundColor': 'rgb(30, 30, 30)',
#                                                             'color': 'dark'
#                                                         },
#                                                         data=local_files,
#                                                         editable=True,
#                                                         #filter_action="native",
#                                                         sort_action="native",
#                                                         sort_mode="multi",
#                                                         column_selectable="single",
#                                                         row_selectable="multi",
#                                                         row_deletable=True,
#                                                         selected_columns=[],
#                                                         selected_rows=[],
#                                                         page_action="native",
#                                                         page_current=0,
#                                                         page_size=30,
#                                                         )),
#         ],
#         id="modal-xl",
#         size="xl",
#         is_open=False,
#     ),
#     dbc.Modal(
#         [
#             dbc.ModalHeader(dbc.ModalTitle(
#                 "Local HW2 Dataset, selected files will be added to batch")),
#             dbc.ModalBody(children=dash_table.DataTable(id='files_table_hw',
#                                                         columns=[
#                                                             {"name": "File name", "id": "fname"}, {
#                                                                 "name": "Dataset", "id": "path"}
#                                                         ],
#                                                         style_header={
#                                                             'backgroundColor': 'rgb(30, 30, 30)',
#                                                             'color': 'dark'
#                                                         },
#                                                         style_data={
#                                                             'backgroundColor': 'rgb(30, 30, 30)',
#                                                             'color': 'dark'
#                                                         },
#                                                         data=local_files_hw,
#                                                         editable=True,
#                                                         #filter_action="native",
#                                                         sort_action="native",
#                                                         sort_mode="multi",
#                                                         column_selectable="single",
#                                                         row_selectable="multi",
#                                                         row_deletable=True,
#                                                         selected_columns=[],
#                                                         selected_rows=[],
#                                                         page_action="native",
#                                                         page_current=0,
#                                                         page_size=30,
#                                                         )),
#         ],
#         id="modal-xl-hw",
#         size="xl",
#         is_open=False,
#     ),
#     dbc.Modal(
#         [
#             dbc.ModalHeader(
#                 dbc.ModalTitle("Start Status"), close_button=True
#             ),
#             dbc.ModalBody(
#                 "Job status: ", id="status"
#             ),
#             dbc.ModalFooter(),
#         ],
#         id="modal-dismiss",
#         #is_open=False,
#     ),
#     dbc.Modal(
#         [
#             dbc.ModalHeader(
#                 dbc.ModalTitle("Job Status"), close_button=True
#             ),
#             dbc.ModalBody(
#                 "Job status: ", id="job_status"
#             ),
#             dbc.ModalFooter(dbc.Button(
#                 'All successed jobs', id='all_jobs', n_clicks=0, style={"margin-left": "5px"})),
#         ],
#         id="modal-job-status",
#         size="xl",
#         #is_open=False,
#     ),
#     dcc.Store(id='intermediate-value')
# ]

movies_table = dash_table.DataTable(id='movies_table', columns=[
    {"name": "URL", "id": "path", "type": "text", "presentation": "markdown"}
    #{"name":"Movie id", "id": "fid", "presentation": "markdown"},{"name":"File name", "id": "fname", "presentation": "markdown"}, {"name": "URL", "id": "path", "type":"text", "presentation": "markdown"}
],
    style_header={
    'backgroundColor': 'rgb(30, 30, 30)',
    'color': 'dark'
},
    style_data={
    'backgroundColor': 'rgb(30, 30, 30)',
    'color': 'dark',
    'whiteSpace': 'normal',
    'height': 'auto',
    'maxWidth': '40px',
    'lineHeight': '15px',
},
    style_cell_conditional=[
    {'if': {'column_id': 'URL'},
     'width': '30px'}
],
    #fixed_rows={'headers': True},
    markdown_options={"html": True},
    data=all_movies,
    editable=False,
    filter_action="native",
    sort_action="native",
    sort_mode="multi",
    column_selectable="single",
    row_selectable="single",
    row_deletable=False,
    selected_columns=[],
    selected_rows=[],
    page_action="native",
    page_current=0,
    page_size=10
)

mdf_carousel = dbc.Carousel(
    items=[
        {"key": "1", "src": "/static/images/slide1.svg"},
        {"key": "2", "src": "/static/images/slide1.svg"},
        {"key": "3", "src": "/static/images/slide1.svg"}
    ],
    controls=False,
    indicators=False,
    id="mdfs_car"
)
mdf_rbuttons = dbc.RadioItems(
    id="mdf-number",
    options=[
        {"label": "MDF 1", "value": 0},
        {"label": "MDF 2", "value": 1},
        {"label": "MDF 3", "value": 2},
    ],
    value=0,
    inline=True,
),

mdf_graph = cyto.Cytoscape(
        id='cytoscape-two-nodes',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '400px'},
        elements=[
            {'data': {'id': 'one', 'label': 'Node 1'}, 'position': {'x': 75, 'y': 75}},
            {'data': {'id': 'two', 'label': 'Node 2'}, 'position': {'x': 200, 'y': 200}},
            {'data': {'source': 'one', 'target': 'two'}}
        ]
    )

mdfs_data = html.Div(
    [
        dbc.Row("Text dddddddddddddddddd ddddddddddddddddddd"),
        dbc.Row(mdf_carousel),
        dbc.Row(mdf_graph),
        dbc.Row(mdf_rbuttons)
    ])


# results_layout = [
#     dbc.Row(
#         [
#             dbc.Col(
#                 [
#                     dcc.Dropdown(pipelines_ok, id='pipelines-dropdown',),
#                     dbc.Button('Refresh movies', id='refresh_movies',
#                                n_clicks=0, style={"margin-top": "5px"}),
#                     dbc.Button('Refresh jobs', id='refresh_jobs',
#                                n_clicks=0, style={"margin-top": "5px"})
#                 ], style={"margin-left": "5px", "margin-right": "50%", "margin-bottom": "20px"})
#         ],
#     ),
#     # dbc.Row(
#     # [
#     #     dbc.Col(movies_table)
#     # ],
#     # ),
#     dbc.Row(
#         [
#             dbc.Col([movies_table]),
#             dbc.Col(id='res_preview_layout',
#                     children="")  # , style={"margin-right": "25%", "margin-left": "25%"})
#         ]
#     ),
#     dbc.Row(
#         [dbc.Button('View results', id='view_results', n_clicks=0)], style={"margin-top": "5px", "margin-right": "85%", "margin-left": "5px"}),
#     dbc.Modal(
#         [
#             dbc.ModalHeader(
#                 dbc.ModalTitle("View MDFS"), close_button=True
#             ),
#             dbc.ModalBody(
#                 mdfs_data, id="mdfs_slider"
#             ),
#             dbc.ModalFooter([""]),
#         ],
#         is_open=False,
#         id="view_mdf",
#         size="xl",
#     )
# ]


# config_layout = [dbc.Row(
#     [
#         dbc.Col([dbc.Input(
#                 id="input_database",
#                 type="url",
#                 placeholder="DB Name",
#                 ),
#         ])
#     ],
# ),
#     dbc.Row(
#     [
#         dbc.Col([dbc.Input(
#                 id="input_web_server",
#                 type="url",
#                 placeholder="Web Server",
#                 ),
#         ])
#     ],
# ),
#     dbc.Row(
#     [
#         dbc.Col([dbc.Input(
#                 id="input_dataset_name",
#                 type="url",
#                 placeholder="Dataset",
#                 ),
#         ])
#     ],
# ),
# ]

main_layout = html.Div(
    [
        dbc.Navbar(dark=True, color="dark", children=[
                   html.H3('NEBULA Project')]),
        dbc.Tabs(
            [
                # dbc.Tab(pipeline_layout, label="Pipeline", tab_id="tab-1",
                #         style={"margin-left": "10%", "margin-right": "20%", "margin-top": "40px"}),
                dbc.Tab(pipeline_view.render_pipeline_content(), label="Pipeline", tab_id="tab-1",
                        style={"margin-left": "10%", "margin-right": "20%", "margin-top": "40px"}),
                # dbc.Tab(results_layout, label="Results Browser", tab_id="tab-2",
                #         style={"margin-left": "10%", "margin-right": "0%", "margin-top": "40px"}),
                dbc.Tab(results_view.render_results_content(pipelines_ok, movies_table, mdfs_data),
                        label="Results Browser", tab_id="tab-2",
                        style={"margin-left": "10%", "margin-right": "0%", "margin-top": "40px"}),
                dbc.Tab(label="Results Statistics", tab_id="tab-3",
                        style={"margin-left": "10%", "margin-right": "0%", "margin-top": "40px"}),
                dbc.Tab(jobs_view.render_jobs_content(), label="Jobs Data", tab_id="tab-4",
                        style={"margin-left": "20%", "margin-right": "10%", "margin-top": "40px"}),
                # dbc.Tab(config_layout, label="Config", style={
                #         "margin-left": "20%", "margin-right": "10%", "margin-top": "40px"}, tab_id="tab-5")
                dbc.Tab(config_view.render_config_content(), label="Config", style={
                        "margin-left": "20%", "margin-right": "10%", "margin-top": "40px"}, tab_id="tab-5")
            ],
            id="tabs",
            active_tab="tab-1",
        ),
        html.Div(id="content"),
        dcc.Store(id='mdfs-data'),
        dcc.Store(id='movie-id')
    ]
)


#app.layout = html.Div(pipeline_layout)
app.layout = main_layout


@app.callback(
    Output("modal-dismiss", "is_open"),
    Output("status", "children"),
    Output('intermediate-value', 'data'),
    [Input("url_s", "n_clicks"), Input('intermediate-value', 'data')],
    [State("modal-dismiss", "is_open")],
)
def toggle_modal(n1, intermediate_value, is_open):
    _js = ""
    print(n1, " ", is_open, " ", intermediate_value)
    if intermediate_value:
        resp_json = intermediate_value
    else:
        resp_json = []
    if n1:
        if len(batch_url_list) != 0:
            print("Start job")
            resp = start_job()
            batch_url_list.clear()
            batch_name_list.clear()
            #print("RESPONCE")
            resp_json.append(resp)
            _js = "Job Started, pipeline id: " + resp['pipeline_id']

        else:
            _js = "Please add URL to batch!"
        batch_name_list.clear()
        batch_url_list.clear()
        return (not is_open, _js, resp_json)
    return (is_open, _js, resp_json)


@app.callback(
    Output("modal-xl-hw", "is_open"),
    #Output('files_table', "selected_rows"),
    Output('files_table', "selected_rows"),
    Input("url_browse_h", "n_clicks"),
    State("modal-xl-hw", "is_open"),
)
def toggle_browser(n1, is_open):
    #print(local_files)
    if n1:
        return not is_open, []
    return is_open, []


@app.callback(
    Output("modal-xl", "is_open"),
    Output('files_table_hw', "selected_rows"),
    #Output('files_table_hw', "selected_rows"),
    Input("url_browse", "n_clicks"),
    State("modal-xl", "is_open"),
)
def toggle_browser_h(n1, is_open):
    #print(local_files)
    if n1:
        return not is_open, []
    return is_open, []


@app.callback(
    Output("modal-job-status", "is_open"),
    #Output("job_status", 'children'),
    Input("url_mon", "n_clicks"),
    #Input('intermediate-value', 'data'),
    State("modal-job-status", "is_open"),
)
def toggle_job_status(n1, is_open):  # , intermediate_value):
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output("job_status", 'children'),
    Input('intermediate-value', 'data'),
    Input("url_mon", "n_clicks"),
)
def return_job_status(intermediate_value, n1):
    #print(intermediate_value)
    status_layout = ""
    status_header = [
        html.Thead(html.Tr([html.Th("Job ID"), html.Th(
            "Job Status"), html.Th("Movie ID"), html.Th("Movie Status")]))
    ]

    #jobs_table = dbc.Table(table_header , bordered=False, dark=True, id='url_table')
    jobs = []
    job_stat = "RUNNING"
    mock_job = 'pipelines/20e23280-d291-421c-a480-ed6e567afe83'
    if len(intermediate_value) > 0:
        for job in intermediate_value:
            movies = []
            mv_stat = "UNKNOW"
            #print(job)
            job_id = job['pipeline_id']
            print(job_id)
            #job_id = mock_job
            jobs_info = db.collection("pipelines").get(job_id)
            if 'tasks' in jobs_info:
                if 'videoprocessing' in jobs_info['tasks']:
                    job_stat = jobs_info['tasks']['videoprocessing']
            row = html.Tr([html.Td(job_id), html.Td(
                job_stat), html.Td(""), html.Td("")])
            jobs.append(row)
            if 'movies' in jobs_info:
                if len(jobs_info['movies']) > 0:
                    print(jobs_info['movies'])
                    for mv in jobs_info['movies']:
                        row_m = html.Tr([html.Td(""), html.Td(""), html.Td(mv), html.Td(
                            jobs_info['movies'][mv]['status']['videoprocessing'])])
                        movies.append(row_m)
                    jobs = jobs + movies
            #for job_info in jobs_info:
        jobs_table = [html.Tbody(jobs)]
        status_layout = dbc.Table(
            status_header + jobs_table, bordered=False, dark=True, id='jobs_table')
        print("STAUS FROM DB ", status_layout)
    return(status_layout)


@app.callback(
    Output("preview_layout", "children"),
    Input("input_url", "value"),
    Input("url_p", component_property='n_clicks')
)
def preview(*val):
    st_layout = [' ']
    if val[0]:
        if "youtu" in val[0]:
            video_or_image[0] = "youtube"
        if val[0].split('.')[-1] == 'mp4' or val[0].split('.')[-1] == 'avi':
            video_or_image[0] = "video"
        else:
            video_or_image[0] = "image"
        if "url_p" == ctx.triggered_id:
            #print("DEBUG ", video_or_image[0])
            if "youtu" in val[0]:
                url_ = YouTube(val[0])
                st_layout = [html.Img(src=url_.thumbnail_url, height=400)]
                video_or_image[0] = "youtube"
                return st_layout
                #print(url_.thumbnail_url)
            if val[0].split('.')[-1] == 'mp4' or val[0].split('.')[-1] == 'avi':
                st_layout = [html.Video(src=val[0], controls=True, height=400)]
                video_or_image[0] = "video"
                return st_layout
            else:
                st_layout = [html.Img(src=val[0], height=400)]
                video_or_image[0] = "movie"
                return st_layout
    else:
        #st_layout = [html.Img(src='https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/Karen_Gillan_as_Nebula.png/220px-Karen_Gillan_as_Nebula.png')]
        return st_layout


@app.callback(
    Output("main_layout", "children"),
    Input("input_url", "value"),
    Input("url_d", component_property='n_clicks'),
    Input("url_s", component_property='n_clicks'),
    Input("url_clean", component_property='n_clicks'),
    Input('files_table', 'derived_virtual_selected_rows'),
    Input('files_table_hw', 'derived_virtual_selected_rows'),
    #Input("v_or_i", component_property='value'),
    prevent_initial_call=True
)
def main_layout(*val):
    print(*val)
    table_body = []
    st_layout = ""
    if "url_s" == ctx.triggered_id:
        st_layout = ['Add new URL\'s to batch ']
        return st_layout
    if "url_clean" == ctx.triggered_id:
        batch_name_list.clear()
        batch_url_list.clear()
        table_body = []
        st_layout = ['Batch list cleared... Add new URL\'s to batch ']
        return st_layout
    if "url_d" == ctx.triggered_id:
        if val[0]:
            row = html.Tr(
                [html.Td(val[0].split("/")[-1]), html.Td(val[0]), "WEB"])
            batch_name_list.append(row)
            batch_url_list.append(val[0])
            table_body = [html.Tbody(batch_name_list)]
        #st_layout = [dbc.Checklist(options=batch_name_list)]
            st_layout = dbc.Table(table_header + table_body,
                                  bordered=False, dark=True, id='url_table')
        return st_layout
    if val[4] or val[5]:
        batch_name_list.clear()
        batch_url_list.clear()
        if val[4]:
            mylist = list(dict.fromkeys(val[4]))
            for r in mylist:
                print(local_files[r]['fname'])
                f_name = local_files[r]['fname'].split("/")[-1]
                row = html.Tr(
                    [html.Td(f_name), html.Td(w_server + f_name), "MSRVTT"])
                batch_name_list.append(row)
                batch_url_list.append(w_server + f_name)
        if val[5]:
            mylist = list(dict.fromkeys(val[5]))
            for r in mylist:
                print(local_files_hw[r]['fname'])
                f_name = local_files_hw[r]['fname'].split("/")[-1]
                row = html.Tr([html.Td(f_name), html.Td(
                    hw2_w_server + f_name), "HW2"])
                batch_name_list.append(row)
                batch_url_list.append(hw2_w_server + f_name)
        table_body = [html.Tbody(batch_name_list)]
        st_layout = dbc.Table(table_header + table_body,
                              bordered=False, dark=True, id='url_table')
        return st_layout
    else:
        print("No video")
        return st_layout


@app.callback(
    Output("res_preview_layout", "children"),
    Output('movie-id', 'data'),
    Input('movies_table', 'derived_virtual_selected_rows'),
)
def preview_res(*val):

    if val[0]:
        movie_idx = val[0][0]
        print(movie_idx)
        st_layout = []
        if 'http' in all_movies[movie_idx]['path']:
            url_path = all_movies[movie_idx]['path']
        else:
            url_path = web_server_prefix + all_movies[movie_idx]['path']
        if url_path.split('.')[-1] == 'mp4' or url_path.split('.')[-1] == 'avi':
            st_layout = [html.Div(dcc.Link(href=url_path, style={"margin-bottom": "15px"})), html.Div(
                html.Video(src=url_path, controls=True, height=300, style={"margin-top": "15px"}))]
            video_or_image[0] = "video"
            return st_layout, all_movies[movie_idx]
        else:
            st_layout = [html.Div(dcc.Link(href=url_path, style={"margin-bottom": "15px"})), html.Div(
                html.Img(src=url_path, height=300, style={"margin-top": "15px"}))]
            # [dcc.Link(href=url_path), html.Img(
            #     src=url_path, height=300, style={"margin-top": "15px"})]
            video_or_image[0] = "image"
            return st_layout, all_movies[movie_idx]
    else:
        return([], {'id': 'Unkonwn'})


@app.callback(
    Output("view_mdf", "is_open"),
    Output("mdfs-data", 'data'),
    Input('view_results', 'n_clicks'),
    #Input('movie-id', 'data'),
    State("view_mdf", "is_open"),
)
def view_mdfs(n1, is_open):
    #print("Data: ", movie_id)
    if n1:
        return not is_open, []
    return is_open, []


@app.callback(
    Output('mdfs_slider', 'children'),
    #Output('mdfs_index', 'children'),
    Input('movie-id', 'data')
)
def return_mdfs_carousel(movie_id):
    mdfs = get_mdfs(movie_id['id'])
    mdf_items = []
    mdf_options = []
    mdf_triplets = []
    mdf_elements = []

    for i, mdf in enumerate(mdfs):
        #print("DEBUG MDF ", mdf)
        mdf_items.append({"key":str(i), "src":mdf['url'],"caption":mdf['candidate'], "header": "Frame number: " + str(mdf['frame_num']), "img_style":{"max-height":"500px"}})#,"max-width":"600px"}})
        mdf_options.append({"label":"MDF: " + str(i), "value": i})
        mdf_triplets.append(mdf['triplets'])


    for i, mdf in enumerate(mdf_triplets):
        for j, triple in enumerate(mdf):
            prev_id = "none"
            for m, node in enumerate(triple):
                print(node)
                id = str(i) + "_" + str(j) + "_" + str(m)
                mdf_elements.append({'data': {'id': id, 'label': node}})
                if prev_id != "none":
                    mdf_elements.append({'data': {'source': prev_id, 'target': id}})
                prev_id = id

    mdf_carousel = dbc.Carousel(
        items=mdf_items,
        #style={"width":"50%","height":"50%"},
        controls=False,
        indicators=False,
        id="mdfs_car"
    )

    mdf_rbuttons = dbc.RadioItems(
        id="mdf-number",
        options=mdf_options,
        value=0,
        inline=True,
    )
    #print(mdf_elements[0])
    mdf_graph = cyto.Cytoscape(
        id='cytoscape-mdf',
        layout={'name': 'concentric'},
        style={'width': '100%', 'height': '400px'},
        elements=mdf_elements
    )

    mdfs_data = html.Div(
        [
            dbc.Row("Movie ID: " + movie_id['id'], style={'margin-top': '20px'}),
            dbc.Row(mdf_carousel, style={'margin-top': '20px'}),
            dbc.Row(mdf_graph, style={'margin-top': '20px'}),
            dbc.Row(mdf_rbuttons, style={'margin-top': '20px'})
        ])
    return(mdfs_data)


@app.callback(
    Output("mdfs_car", "active_index"),
    Input("mdf-number", "value"),
)
def select_slide(idx):
    print(idx)
    return idx


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8060, debug=True),
