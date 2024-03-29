import dash_bootstrap_components as dbc
from dash import html
from dash import dcc

from callbacks.golden_angles import *
from callbacks.utilities.initialization import init_app_about

app_name = 'golden_angles'
app_id_dict = init_app_ids(app_name=app_name)

layout = html.Div([
    dbc.Row([html.H2("Golden Angles",
                     style=({'color': 'blue'}),
                     ),
             ],
            class_name='title_tools',
            ),
    html.Hr(style={'borderTop': '3px solid blue'}),
    init_app_about(current_app=app_name, app_id_dict=app_id_dict),
    html.Div(
        [
            html.Br(),
            dbc.Row([
                dbc.Col(lg=1),
                dbc.Label("Max angle value: "),
                dcc.RadioItems(
                    id='max_angle',
                    options=[
                        {'label': u"180\u00b0", 'value': 180},
                        {'label': u"360\u00b0", 'value': 360}
                    ],
                    value=180,
                    labelStyle={'display': 'inline-block'},
                    style={"padding": "0px",
                           "margin-left": "10px"
                           },
                ),
            ]),
            dbc.Row([
                dbc.Col(lg=1),
                dbc.Label("Number of angles:"),
                dcc.Input(id="number_of_angles",
                          type="number",
                          min=1,
                          value=50),
            ]),
            html.Br(),
            dbc.Tabs([
                dbc.Tab([
                    html.Div(id='table')
                ], label='Data'),
                dbc.Tab([
                    dcc.Graph(id='plot',
                              config={'displaylogo': False,
                                      })

                ], label='Plot')
            ]),
        ])
],
    style={'margin': '25px'}

)
