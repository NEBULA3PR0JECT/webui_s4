from dash import Dash, dcc, html, ctx, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import time
from pytube import YouTube 
import glob
import base64
import requests
from gradient import WorkflowsClient
import yaml

w_server = 'http://74.82.29.209:9000/msrvtt/'
j_status = []
j_status.append("")
app = Dash(__name__,external_stylesheets=[dbc.themes.SLATE])
image_filename = 'marvel-nebula-png-picture-stock-nebula-guardians-of-the-galaxy-cartoo-11562973029avtizra9bu.png' # replace with your own image
#encoded_image = base64.b64encode(open(image_filename, 'rb').read())
#print(encoded_image)
local_files = []
for i in glob.glob("/datasets/msrvtt/*"):
    #print(local_files)
    local_files.append({"fname": i, "path":"msrvtt"})
local_files_hw = []
for i in glob.glob("//datasets/hollywood2/Hollywood2/AVIClips/*"):
    #print(local_files)
    local_files_hw.append({"fname": i, "path":"hw2"})
video_or_image_lable = "Image/Video"
video_or_image = []
video_or_image.append('video')
batch_url_list = []
batch_name_list = []
#local_files = []

def start_job_rest():
    movies = []
    headers = {'Content-type': 'application/json'}
    for movie in batch_url_list:
        _movie = {"movie_id": "", "url": movie, "type": "file"}
        movies.append(_movie)
    payload = {"movies": movies,
    "save_movies": 'true', # if you want to save movies/frames on disk
    "output" : "db",
    "is_async": 'true',
    "overwrite": 'true' # to overwrite existing results - re-run
    }
    print(payload)
    response = requests.post('http://74.82.28.218:48005/process/movies', json=payload, headers=headers)
    return response.json()

def start_job():
    gk = '5d88bfa5909b30076829c101624d67'

    workflow_client = WorkflowsClient(gk)

    spec_path = "./workflow-spec.yaml"

    yaml_spec = open(spec_path, 'r')
    spec = yaml.safe_load(yaml_spec)

    print(workflow_client.run_workflow(
        workflow_id='553d666c-2306-4bf3-a3db-9bd1275a9657',
        spec=spec,
        cluster_id='clg07azjl',
        inputs=None
    ))

table_header = [
    html.Thead(html.Tr([html.Th("File"), html.Th("URL"), html.Th("Source")]))
]
st_layout = dbc.Table(table_header , bordered=False, dark=True, id='url_table')

app.layout = html.Div(
    [
        dbc.Navbar(dark = True, color="dark",children=[html.H3('NEBULA3 Pipeline')]),
        dbc.Row(dbc.Col(html.H1(style={"margin-left": "30%", "margin-top": "25px"},children=''))), 
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
                dbc.Col(dbc.ButtonGroup(children=
                    [
                    dbc.Button('Preview Video/Image', id='url_p', n_clicks=0)
                    #dbc.Button('Add to batch', id='url_d', n_clicks=0, style={"margin-left": "5px"})
                    # dbc.Button('Clean Batch', id='url_clean', n_clicks=0, style={"margin-left": "5px"}),
                    # dbc.Button('Browse Files', id='url_modal', n_clicks=0, style={"margin-left": "5px"}),
                    # dbc.Button('Start Pipeline', id='url_s', n_clicks=0, style={"margin-left": "5px"})
                    ]))
                #dbc.Col()
            ],
            style={"margin-top": "25px", "margin-left": "15%"}
        ),
        dbc.Row(
            [
                dbc.Col(id='preview_layout',style={"margin-left": "15%","margin-right": "15%","margin-top":"20px"}, 
                children="")
            ]
        ),
        dbc.Row(
            [
               dbc.Col(
                [
                    dbc.ButtonGroup(children=
                    [
                    dbc.Button('Add to batch', id='url_d', n_clicks=0),
                    dbc.Button('Clean Batch', id='url_clean', n_clicks=0, style={"margin-left": "5px"}),
                    #dbc.Button('Browse Files', id='url_browse', n_clicks=0, style={"margin-left": "5px"}),
                    dbc.Button('Start Pipeline', id='url_s', n_clicks=0, style={"margin-left": "100px"}),
                    dbc.Button('Jobs status', id='url_mon', n_clicks=0, style={"margin-left": "5px"})
                    ]),
                    dbc.ButtonGroup(children=
                    [
                    dbc.Button('Browse MSRVTT', id='url_browse', n_clicks=0, style={"margin-left": "100px"}),
                    dbc.Button('Browse HW2', id='url_browse_h', n_clicks=0, style={"margin-left": "5px"})
                    ])
                ]    
                )
            ],
            style={"margin-top": "25px", "margin-left": "15%"}
        ),
        dbc.Row(
            [
                dbc.Col(id='main_layout',style={"margin-left": "15%","margin-right": "40%","margin-top":"20px"}, 
                children=dbc.Table(table_header, bordered=False, dark=True, id='url_table'))
            ]
        ),      
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Local Dataset MSRVTT, selected files will be added to batch")),
                dbc.ModalBody(children= dash_table.DataTable(id='files_table',
                columns=[
                        {"name":"File name", "id": "fname"}, {"name": "Dataset", "id": "path"}
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
                        page_current= 0,
                        page_size= 30,
                )),
            ],
            id="modal-xl",
            size="xl",
            is_open=False,
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Local HW2 Dataset, selected files will be added to batch")),
                dbc.ModalBody(children= dash_table.DataTable(id='files_table_hw',
                columns=[
                        {"name":"File name", "id": "fname"}, {"name": "Dataset", "id": "path"}
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
                        page_current= 0,
                        page_size= 30,
                )),
            ],
            id="modal-xl-hw",
            size="xl",
            is_open=False,
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle("Status"), close_button=True
                ),
                dbc.ModalBody(
                    "Job status: ", id="status"
                ),
                dbc.ModalFooter(),
            ],
            id="modal-dismiss",
            #is_open=False,
        )
    ]
)

@app.callback(
    Output("modal-dismiss", "is_open"),
    Output("status","children"),
    [Input("url_s", "n_clicks")],
    [State("modal-dismiss", "is_open")],
)
def toggle_modal(n1, is_open):
    _js = ""
    if n1:
        if len(batch_url_list) != 0:
            _js = "Job Started"
            print("Start job")
            resp = start_job()
            batch_url_list.clear()
            print(resp)
        else:
            _js = "Please add URL to batch!"
        return (not is_open,_js)
    return (is_open,_js)

@app.callback(
    Output("modal-xl-hw", "is_open"),
    Input("url_browse_h", "n_clicks"),
    State("modal-xl-hw", "is_open"),
)
def toggle_browser(n1, is_open):
    #print(local_files)
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output("modal-xl", "is_open"),
    Input("url_browse", "n_clicks"),
    State("modal-xl", "is_open"),
)
def toggle_browser_h(n1, is_open):
    #print(local_files)
    if n1:
        return not is_open
    return is_open
# @app.callback(Output('v_or_i', 'disabled'),
#              Input("url_d", component_property='n_clicks'),
#              Input("url_clean", component_property='n_clicks'))
# def set_button_enabled_state(on_, off_):
#     if "url_d" == ctx.triggered_id:
#         return True
#     if "url_clean" == ctx.triggered_id:
#         return False

# @app.callback(
#     Output("standalone-radio-check-output","children"),
#     Input("v_or_i", component_property='value')

# )
# def switch_layout(*val):
#     if val[0]:
#         video_or_image.clear()
#         video_or_image.append("Video")
#         return "Processing Video..."
#     else:
#         print("Image")
#         video_or_image.clear()
#         video_or_image.append("Image")
#         return "Processing Image/Frame..."

@app.callback(
    Output("preview_layout", "children"),
    Input("input_url", "value"),
    Input("url_p", component_property='n_clicks')
    )
def preview(*val):
    print(val)
    st_layout = [' ']
    if val[0]:
        if "url_p" == ctx.triggered_id:
            #print("DEBUG ", video_or_image[0])
            if "youtu" in val[0]:
                url_ = YouTube(val[0])
                st_layout = [html.Img(src=url_.thumbnail_url, height=600)]
                video_or_image[0] = "youtube"
                return st_layout
                #print(url_.thumbnail_url)
            if val[0].split('.')[-1] == 'mp4' or val[0].split('.')[-1] == 'avi':
                st_layout = [html.Video(src=val[0],controls=True, height=600)]
                video_or_image[0] = "video"
                return st_layout
            else:
                st_layout = [html.Img(src=val[0], height=600)]
                video_or_image[0] = "image"
                return st_layout 
    else:
        #st_layout = [html.Img(src='https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/Karen_Gillan_as_Nebula.png/220px-Karen_Gillan_as_Nebula.png')]
        return st_layout

# @app.callback(
#     Output("main_layout", "children"),
#     Input('files_table', 'selected_columns')
# )
# def return_files(selected_columns):
#     for i in selected_columns:
#         print(i)
#     return()

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
    table_body = [html.Tbody(batch_name_list)]
    st_layout = dbc.Table(table_header + table_body, bordered=False, dark=True, id='url_table')
    if "url_clean" == ctx.triggered_id or "url_s" == ctx.triggered_id :
        batch_name_list.clear()
        batch_url_list.clear()
        st_layout = ['Batch list cleared... Add new URL\'s to batch ']
        return st_layout
    if "url_d" == ctx.triggered_id:
        if val[0]:
            row = html.Tr([html.Td( val[0].split("/")[-1]), html.Td( val[0]),"WEB"])
            batch_name_list.append(row)
            batch_url_list.append(val[0])
            table_body = [html.Tbody(batch_name_list)]
        #st_layout = [dbc.Checklist(options=batch_name_list)]
            st_layout = dbc.Table(table_header + table_body, bordered=False, dark=True, id='url_table')
        return st_layout
    if val[4] or val[5]:
        batch_name_list.clear()
        if val[4]:  
            for r in val[4]:
                print(local_files[r]['fname'])
                f_name = local_files[r]['fname'].split("/")[-1]
                row = html.Tr([html.Td(f_name), html.Td(w_server + f_name),"MSRVTT"])
                batch_name_list.append(row)
            #table_body = [html.Tbody(batch_name_list)]
            #st_layout = dbc.Table(table_header + table_body, bordered=False, dark=True, id='url_table')
            #return st_layout
        if val[5]:
            for r in val[5]:
                print(local_files_hw[r]['fname'])
                f_name = local_files_hw[r]['fname'].split("/")[-1]
                row = html.Tr([html.Td(f_name), html.Td(w_server + f_name),"MSRVTT"])
                batch_name_list.append(row)
        table_body = [html.Tbody(batch_name_list)]
        st_layout = dbc.Table(table_header + table_body, bordered=False, dark=True, id='url_table')
        return st_layout
    else:
        print("No video")
        return st_layout
    


if __name__ == "__main__":
    app.run_server(host="0.0.0.0",debug=True ), 
