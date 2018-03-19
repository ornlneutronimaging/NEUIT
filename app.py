from model import InitForm
from model import SampleForm
import flask
from flask import render_template, request
from compute import init_reso, add_layer, load_beam_shape
from flask import Flask
import io
import os
import matplotlib.pyplot as plt
import base64
from scipy.interpolate import interp1d
from ImagingReso.resonance import Resonance
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pprint
from ImagingReso._utilities import ev_to_angstroms
from ImagingReso._utilities import ev_to_s
import math

# Setup app
server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')

app = dash.Dash(__name__)
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

# Create app layout
app.layout = html.Div(
    [
        # Heading section
        html.Div(
            [
                html.H1(
                    children='ImagingReso',
                    className='nine columns'
                ),
                html.Img(
                    src="http://static1.squarespace.com/static/546fb494e4b08c59a7102fbc/t/591e105a6a496334b96b8e47/1497495757314/.png",
                    className='three columns',
                    style={
                        'height': '7%',
                        'width': '7%',
                        'float': 'right',
                        'position': 'relative',
                        'padding-top': 0,
                        'padding-right': 0
                    },
                ),
            ], className="row"
        ),
        html.Div(
            children='''
                A web application for *Neutron Imaging*.
                ''',
            className='row'
        ),
        html.H3('Global parameters'),
        # Global parameters
        html.Div(
            [
                # Range input
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Checklist(id='check_energy',
                                              options=[
                                                  {'label': 'Energy (eV)', 'value': True, 'disabled': True},
                                              ],
                                              values=[True],
                                              labelStyle={'display': 'inline-block'}
                                              ),
                                html.Div(
                                    [
                                        dcc.Input(id='e_min', type='number', value=1, min=0,
                                                  inputmode='numeric',
                                                  step=1,
                                                  ),
                                        dcc.Input(id='e_max', type='number', value=100, max=1e5,
                                                  inputmode='numeric',
                                                  step=1,
                                                  ),
                                    ]
                                ),
                            ],
                            className='two columns',
                        ),

                        html.Div(
                            [
                                dcc.Checklist(id='check_lambda',
                                              options=[
                                                  {'label': 'Wavelength (\u212B)', 'value': True},
                                              ],
                                              values=[],
                                              labelStyle={'display': 'inline-block'}
                                              ),
                                html.Div(id='range_lambda'),
                            ],
                            className='two columns',
                        ),

                        html.Div(
                            [

                                dcc.Checklist(id='check_tof',
                                              options=[
                                                  {'label': 'Time-of-flight (\u03BCs)', 'value': True},
                                              ],
                                              values=[],
                                              labelStyle={'display': 'inline-block'}
                                              ),
                                html.Div(id='range_tof'),
                            ],
                            className='two columns',
                        ),

                        html.Div(
                            [
                                html.P('Source-to-detector (m)'),
                                # html.P('(ONLY for TOF)'),
                                dcc.Input(id='distance', type='number', value=16.45, min=1,
                                          inputmode='numeric',
                                          step=0.01,
                                          # size=5
                                          # className='six columns',
                                          )
                            ],
                            className='two columns',
                        ),

                    ], className='row',
                ),

                # html.Br(),

                # Step input
                html.Div(
                    [
                        html.Div(
                            [
                                html.P('Step in energy (eV)'),
                                # dcc.Input(id='e_step', type='number', value=0.01, min=0.001, max=1),
                                dcc.Dropdown(
                                    id='e_step',
                                    options=[
                                        {'label': '0.001', 'value': 0.001},
                                        {'label': '0.01', 'value': 0.01},
                                        {'label': '0.1', 'value': 0.1},
                                        {'label': '1', 'value': 1},
                                        {'label': '10', 'value': 10},
                                        {'label': '100', 'value': 100},
                                    ],
                                    value=0.01,
                                    searchable=False,
                                    clearable=False,
                                    # placeholder="Pick a step size",
                                )
                            ], className='two columns'
                        ),

                        html.Div(
                            [
                                # Energy slider
                                # html.P('Energy range slider'),
                                html.Br(),
                                dcc.RangeSlider(
                                    id='e_range_slider',
                                    min=-5,
                                    max=6,
                                    value=[0, 2],
                                    allowCross=False,
                                    dots=False,
                                    step=0.01,
                                    # updatemode='drag'
                                    marks={i: '{} eV'.format(pow(10, i)) for i in range(-5, 7, 1)},
                                    className='row',
                                ),
                            ], className='eight columns'
                        ),
                    ], className='row'
                ),
            ]
        ),

        html.H3('Sample info'),

        # Sample input
        html.Div(
            [
                html.Div(
                    [
                        html.P('Layer', className='one columns'),
                        html.P('Chemical formula', className='two columns'),
                        html.P('Thickness (mm)', className='two columns'),
                        html.P('Density (g/cm^3)', className='two columns'),
                        html.P('Omit density?', className='two columns'),
                    ], className='row',
                ),

                html.Div(
                    [
                        html.P(id='text_1', children='1', className='one columns'),
                        dcc.Input(id='formula_1', value='Ag', type='text', minlength=1, className='two columns'),
                        dcc.Input(id='thickness_1', value=0.5, type='number', min=0, inputmode="numeric",
                                  step=0.001, className='two columns'),
                        dcc.Input(id='density_1', type='number', min=0, step=0.001, className='two columns'),
                        dcc.Checklist(id='omit_density_1', options=[{'value': True}], values=[True],
                                      className='two columns'),
                    ], className='row'
                ),

                html.Div(
                    [
                        html.P(id='text_2', children='2', className='one columns'),
                        dcc.Input(id='formula_2', type='text', minlength=1, className='two columns'),
                        dcc.Input(id='thickness_2', type='number', min=0, inputmode="numeric",
                                  step=0.001, className='two columns'),
                        dcc.Input(id='density_2', type='number', min=0, step=0.001, className='two columns'),
                        dcc.Checklist(id='omit_density_2', options=[{'value': True}], values=[True],
                                      className='two columns'),
                    ], className='row'
                ),

                html.Div(
                    [
                        html.P(id='text_3', children='3', className='one columns'),
                        dcc.Input(id='formula_3', type='text', minlength=1, className='two columns'),
                        dcc.Input(id='thickness_3', type='number', min=0, inputmode="numeric",
                                  step=0.001, className='two columns'),
                        dcc.Input(id='density_3', type='number', min=0, step=0.001, className='two columns'),
                        dcc.Checklist(id='omit_density_3', options=[{'value': True}], values=[True],
                                      className='two columns'),
                    ], className='row'
                ),

                # html.Div(id='more_sample'),

                html.P(
                    'NOTE: density can be omitted ONLY if the input sample is under standard condition and contains 1 element.'
                ),

                html.Div(

                ),

                html.Div(
                    [
                        # html.Button('Add layer', id='button_add', className='three columns'),
                        # html.Button('Delete layer', id='button_del', className='three columns'),
                        html.Button('Submit', id='button_submit', className='three columns'),
                    ], className='row'
                ),
            ]
        ),

        html.Hr(),
        # Transmission at CG-1D
        html.Div(id='result'),
        # Plot control buttons
        html.Div(
            [
                html.Div(
                    [
                        html.P('X options: ', className='two columns'),
                        dcc.RadioItems(id='x_type',
                                       options=[
                                           {'label': 'Energy', 'value': 'energy'},
                                           {'label': 'Wavelength', 'value': 'lambda'},
                                           {'label': 'Time', 'value': 'time'},
                                       ],
                                       value='energy',
                                       labelStyle={'display': 'inline-block'},
                                       className='six columns',
                                       )
                    ], className='row'
                ),
                html.Div(
                    [
                        html.P('Y options: ', className='two columns'),
                        dcc.RadioItems(id='y_type',
                                       options=[
                                           {'label': 'Attenuation', 'value': 'attenuation'},
                                           {'label': 'Transmission', 'value': 'transmission'},
                                           {'label': 'Total cross-section', 'value': 'sigma'}
                                       ],
                                       value='attenuation',
                                       labelStyle={'display': 'inline-block'},
                                       className='six columns',
                                       )
                    ], className='row'
                ),
                html.Div(
                    [
                        html.P('Scale options: ', className='two columns'),
                        dcc.RadioItems(id='plot_scale',
                                       options=[
                                           {'label': 'Linear', 'value': 'linear'},
                                           {'label': 'Log x', 'value': 'logx'},
                                           {'label': 'Log y', 'value': 'logy'},
                                           {'label': 'Loglog', 'value': 'loglog'},
                                       ],
                                       value='linear',
                                       labelStyle={'display': 'inline-block'},
                                       className='six columns',
                                       )
                    ], className='row'
                ),
                html.Div(
                    [
                        html.P('Show isotope: ', className='two columns'),
                        dcc.Checklist(id='show_iso',
                                      options=[{'value': True}], values=[],
                                      className='six columns',
                                      )
                    ], className='row'
                ),
            ]
        ),
        # Plot
        html.Div(id='plot'),

        # Debug region
        html.Hr(),
        html.Div(
            [
                html.Div(id='stack'),
            ],
        ),
    ], className='ten columns offset-by-one'
)


@app.callback(
    Output('range_lambda', 'children'),
    [
        Input('check_lambda', 'values'),
        Input('e_min', 'value'),
        Input('e_max', 'value'),
    ])
def show_range_in_lambda(boo, e_min, e_max):
    if boo:
        lambda_1 = ev_to_angstroms(array=e_min)
        lambda_2 = ev_to_angstroms(array=e_max)
        return html.Div(
            [
                dcc.Input(id='lambda_1', type='number', value=lambda_1, inputmode='numeric', step=0.01),
                dcc.Input(id='tambda_2', type='number', value=lambda_2, inputmode='numeric', step=0.01),
            ]
        )


@app.callback(
    Output('range_tof', 'children'),
    [
        Input('check_tof', 'values'),
        Input('distance', 'value'),
        Input('e_min', 'value'),
        Input('e_max', 'value'),
    ])
def show_range_in_tof(boo, distance, e_min, e_max):
    if boo:
        tof_1 = ev_to_s(array=e_min, source_to_detector_m=distance, offset_us=0) * 1e6
        tof_2 = ev_to_s(array=e_max, source_to_detector_m=distance, offset_us=0) * 1e6
        return html.Div(
            [
                dcc.Input(id='tof_1', type='number', value=tof_1, inputmode='numeric', step=1),
                dcc.Input(id='tof_2', type='number', value=tof_2, inputmode='numeric', step=1),
            ]
        )


@app.callback(
    Output('e_min', 'value'),
    [
        Input('e_range_slider', 'value'),
    ])
def update_e_min_from_slider(slider):
    transformed_value = [pow(10, v) for v in slider]
    _min = transformed_value[0]
    # if _min != min_input:
    #     return _min
    return _min


@app.callback(
    Output('e_max', 'value'),
    [
        Input('e_range_slider', 'value'),
    ])
def update_e_max_from_slider(slider):
    transformed_value = [pow(10, v) for v in slider]
    _max = transformed_value[1]
    # if _max != max_input:
    #     return _max
    return _max


@app.callback(
    Output('plot_scale', 'options'),
    [
        Input('y_type', 'value'),
    ])
def disable_logx_when_not_plot_sigma(y_type):
    if y_type != 'sigma':
        options = [
            {'label': 'Linear', 'value': 'linear'},
            {'label': 'Log x', 'value': 'logx'},
        ]
    else:
        options = [
            {'label': 'Linear', 'value': 'linear'},
            {'label': 'Log x', 'value': 'logx'},
            {'label': 'Log y', 'value': 'logy'},
            {'label': 'Loglog', 'value': 'loglog'},
        ]
    return options


# @app.callback(
#     Output('show_iso', 'values'),
#     [
#         Input('y_type', 'value'),
#     ])
# def enable_iso_when_plot_sigma(y_type):
#     if y_type == 'sigma':
#         return [True]


@app.callback(
    Output('density_1', 'value'),
    [
        Input('button_submit', 'n_clicks'),
    ],
    [
        State('e_min', 'value'),
        State('e_max', 'value'),
        State('e_step', 'value'),
        State('formula_1', 'value'), State('thickness_1', 'value'),
        State('density_1', 'value'), State('omit_density_1', 'values'),
    ])
def upadate_density(n_clicks, e_min, e_max, e_step,
                    formula_1, thickness_1, density_1, omit_density_1,
                    ):
    o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
    if omit_density_1:
        o_reso.add_layer(formula=formula_1,
                         thickness=thickness_1)
    else:
        o_reso.add_layer(formula=formula_1,
                         thickness=thickness_1,
                         density=density_1)
    stack = o_reso.stack
    # for each_layer in stack.keys():
    #     _density = stack[each_layer]['density']['value']
    layer = list(stack.keys())
    _density = stack[layer[0]]['density']['value']
    if n_clicks is not None:
        return _density


@app.callback(
    Output('density_2', 'value'),
    [
        Input('button_submit', 'n_clicks'),
    ],
    [
        State('e_min', 'value'),
        State('e_max', 'value'),
        State('e_step', 'value'),
        State('formula_2', 'value'), State('thickness_2', 'value'),
        State('density_2', 'value'), State('omit_density_2', 'values'),
    ])
def upadate_density(n_clicks, e_min, e_max, e_step,
                    formula_2, thickness_2, density_2, omit_density_2,
                    ):
    o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
    if formula_2 is not None and thickness_2 is not None:
        if omit_density_2:
            o_reso.add_layer(formula=formula_2,
                             thickness=thickness_2)
        else:
            o_reso.add_layer(formula=formula_2,
                             thickness=thickness_2,
                             density=density_2)
    stack = o_reso.stack
    layer = list(stack.keys())
    _density = stack[layer[0]]['density']['value']
    if n_clicks is not None:
        return _density


@app.callback(
    Output('density_3', 'value'),
    [
        Input('button_submit', 'n_clicks'),
    ],
    [
        State('e_min', 'value'),
        State('e_max', 'value'),
        State('e_step', 'value'),
        State('formula_3', 'value'), State('thickness_3', 'value'),
        State('density_3', 'value'), State('omit_density_3', 'values'),
    ])
def upadate_density(n_clicks, e_min, e_max, e_step,
                    formula_3, thickness_3, density_3, omit_density_3,
                    ):
    o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
    if formula_3 is not None and thickness_3 is not None:
        if omit_density_3:
            o_reso.add_layer(formula=formula_3,
                             thickness=thickness_3)
        else:
            o_reso.add_layer(formula=formula_3,
                             thickness=thickness_3,
                             density=density_3)
    stack = o_reso.stack
    layer = list(stack.keys())
    _density = stack[layer[0]]['density']['value']
    if n_clicks is not None:
        return _density


@app.callback(
    Output('plot', 'children'),
    [
        Input('button_submit', 'n_clicks'),
        Input('y_type', 'value'),
        Input('x_type', 'value'),
        Input('plot_scale', 'value'),
        Input('show_iso', 'values'),
    ],
    [
        State('e_min', 'value'),
        State('e_max', 'value'),
        State('e_step', 'value'),
        State('distance', 'value'),
        State('formula_1', 'value'), State('thickness_1', 'value'),
        State('density_1', 'value'), State('omit_density_1', 'values'),
        State('formula_2', 'value'), State('thickness_2', 'value'),
        State('density_2', 'value'), State('omit_density_2', 'values'),
        State('formula_3', 'value'), State('thickness_3', 'value'),
        State('density_3', 'value'), State('omit_density_3', 'values'),
    ])
def plot(n_clicks,
         y_type, x_type, plot_scale, show_iso,
         e_min, e_max, e_step, distance_m,
         formula_1, thickness_1, density_1, omit_density_1,
         formula_2, thickness_2, density_2, omit_density_2,
         formula_3, thickness_3, density_3, omit_density_3,
         ):
    o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
    if omit_density_1:
        o_reso.add_layer(formula=formula_1,
                         thickness=thickness_1)
    else:
        o_reso.add_layer(formula=formula_1,
                         thickness=thickness_1,
                         density=density_1)
    if formula_2 is not None and thickness_2 is not None:
        if omit_density_2:
            o_reso.add_layer(formula=formula_2,
                             thickness=thickness_2)
        else:
            o_reso.add_layer(formula=formula_2,
                             thickness=thickness_2,
                             density=density_2)
    if formula_3 is not None and thickness_3 is not None:
        if omit_density_3:
            o_reso.add_layer(formula=formula_3,
                             thickness=thickness_3)
        else:
            o_reso.add_layer(formula=formula_3,
                             thickness=thickness_3,
                             density=density_3)
    if plot_scale == 'logx':
        _log_x = True
        _log_y = False
    elif plot_scale == 'logy':
        _log_x = False
        _log_y = True
    elif plot_scale == 'loglog':
        _log_x = True
        _log_y = True
    else:
        _log_x = False
        _log_y = False
    if show_iso is None:
        show_iso = False
    plotly_fig = o_reso.plot(plotly=True,
                             y_axis=y_type,
                             x_axis=x_type,
                             time_unit='us',
                             logy=_log_y,
                             logx=_log_x,
                             all_elements=True,
                             all_isotopes=show_iso,
                             source_to_detector_m=distance_m)
    plotly_fig.layout.showlegend = True

    if n_clicks is not None:
        return html.Div(
            [
                dcc.Graph(id='reso_plot', figure=plotly_fig)
            ]
        )


@app.callback(
    Output('result', 'children'),
    [
        Input('button_submit', 'n_clicks'),
    ],
    [
        State('y_type', 'value'),
        State('formula_1', 'value'), State('thickness_1', 'value'),
        State('density_1', 'value'), State('omit_density_1', 'values'),
        State('formula_2', 'value'), State('thickness_2', 'value'),
        State('density_2', 'value'), State('omit_density_2', 'values'),
        State('formula_3', 'value'), State('thickness_3', 'value'),
        State('density_3', 'value'), State('omit_density_3', 'values'),
    ])
def calculate_transmission_cg1d(n_clicks, y_type,
                                formula_1, thickness_1, density_1, omit_density_1,
                                formula_2, thickness_2, density_2, omit_density_2,
                                formula_3, thickness_3, density_3, omit_density_3,
                                ):
    _main_path = os.path.abspath(os.path.dirname(__file__))
    _path_to_beam_shape = os.path.join(_main_path, 'static/instrument_file/beam_shape_cg1d.txt')
    df = load_beam_shape(_path_to_beam_shape)
    o_reso = init_reso(e_min=0.00025,
                       e_max=0.12525,
                       e_step=0.000625)
    if omit_density_1:
        o_reso.add_layer(formula=formula_1,
                         thickness=thickness_1)
    else:
        o_reso.add_layer(formula=formula_1,
                         thickness=thickness_1,
                         density=density_1)
    if formula_2 is not None and thickness_2 is not None:
        if omit_density_2:
            o_reso.add_layer(formula=formula_2,
                             thickness=thickness_2)
        else:
            o_reso.add_layer(formula=formula_2,
                             thickness=thickness_2,
                             density=density_2)
    if formula_3 is not None and thickness_3 is not None:
        if omit_density_3:
            o_reso.add_layer(formula=formula_3,
                             thickness=thickness_3)
        else:
            o_reso.add_layer(formula=formula_3,
                             thickness=thickness_3,
                             density=density_3)
    # interpolate with the beam shape energy ()
    interp_type = 'cubic'
    energy = o_reso.total_signal['energy_eV']
    trans = o_reso.total_signal['transmission']
    interp_function = interp1d(x=energy, y=trans, kind=interp_type)
    # add interpolated transmission value to beam shape df
    trans = interp_function(df['energy_eV'])
    # calculated transmitted flux
    trans_flux = trans * df['flux']
    stack = o_reso.stack
    # stack = pprint.pformat(o_reso.stack)

    _total_trans = sum(trans_flux) / sum(df['flux']) * 100
    total_trans = round(_total_trans, 3)
    if n_clicks is not None:
        if y_type == 'transmission':
            return html.Div(
                [
                    # html.H3('Result'),
                    html.H4('Sample transmission'),
                    html.P('The total neutron transmission at CG-1D: {} %'.format(total_trans))
                ]
            )
        else:
            return html.Div(
                [
                    # html.H3('Result'),
                    html.H4('Sample attenuation'),
                    html.P('The total neutron attenuation at CG-1D: {} %'.format(100 - total_trans))
                ]
            )


@app.callback(
    Output('stack', 'children'),
    [
        # Input('button_add', 'n_clicks'),
        # Input('button_del', 'n_clicks'),
        Input('button_submit', 'n_clicks'),
    ],
    [
        State('e_min', 'value'),
        State('e_max', 'value'),
        State('e_step', 'value'),
        State('formula_1', 'value'), State('thickness_1', 'value'),
        State('density_1', 'value'), State('omit_density_1', 'values'),
        State('formula_2', 'value'), State('thickness_2', 'value'),
        State('density_2', 'value'), State('omit_density_2', 'values'),
        State('formula_3', 'value'), State('thickness_3', 'value'),
        State('density_3', 'value'), State('omit_density_3', 'values'),
        # State('more_sample', 'value'),
    ])
def compute(n_clicks, e_min, e_max, e_step,
            formula_1, thickness_1, density_1, omit_density_1,
            formula_2, thickness_2, density_2, omit_density_2,
            formula_3, thickness_3, density_3, omit_density_3,
            ):
    # if n_clicks is not None:
    o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)

    # if density is not None:
    if omit_density_1:
        o_reso.add_layer(formula=formula_1,
                         thickness=thickness_1)
    else:
        o_reso.add_layer(formula=formula_1,
                         thickness=thickness_1,
                         density=density_1)
    if formula_2 is not None and thickness_2 is not None:
        if omit_density_2:
            o_reso.add_layer(formula=formula_2,
                             thickness=thickness_2)
        else:
            o_reso.add_layer(formula=formula_2,
                             thickness=thickness_2,
                             density=density_2)
    if formula_3 is not None and thickness_3 is not None:
        if omit_density_3:
            o_reso.add_layer(formula=formula_3,
                             thickness=thickness_3)
        else:
            o_reso.add_layer(formula=formula_3,
                             thickness=thickness_3,
                             density=density_3)
    stack = o_reso.stack
    p_stack = pprint.pformat(o_reso.stack)
    layer = list(stack.keys())
    for each_layer in stack.keys():
        current_layer = stack[each_layer]
        elements = current_layer['elements']
        # pprint.pprint(children[0]['props']['children'][3]['props'])
    return [
        html.P("Stack: {}".format(p_stack)),
        html.P("Layer: {}".format(layer)),
        html.P("Element: {}".format(elements)),
        html.P("Submit clicks: {}".format(n_clicks)),
        # html.P("Add clicks: {}".format(n_add)),
        # html.P("Del clicks: {}".format(n_del)),
        html.P("e_min_slider: {}".format(e_min)),
        html.P("e_max_slider: {}".format(e_max)),
        html.P("e_step_slider: {}".format(e_step)),
    ]


# @app.callback(Output('more_sample', 'children'),
#               [
#                   Input('button_add', 'n_clicks'),
#                   Input('button_del', 'n_clicks'),
#                   # Input('button_reset', 'n_clicks'),
#               ])
# def more_layer(n_add, n_del):
#     if n_add is None:
#         n_add = 0
#     if n_del is None:
#         n_del = 0
#     if n_del > n_add:
#         n_diff = n_del - n_add
#         n_add = n_add + n_diff
#     n_row = n_add - n_del
#     n_row = n_row + 1
#     div_list = []
#     for n in range(n_row):
#         current_div = html.Div(
#             [
#                 html.P(id='text_' + str(n + 1), children=str(n + 1), className='one columns'),
#                 dcc.Input(id='formula_' + str(n + 1), type='text', minlength=1, className='two columns'),
#                 dcc.Input(id='thickness_' + str(n + 1), type='number', min=0, inputmode="numeric",
#                           step=0.01, className='two columns'),
#                 dcc.Input(id='density_' + str(n + 1), type='number', min=0, step=0.001, value=1,
#                           className='two columns'),
#                 dcc.Checklist(id='omit_density_' + str(n + 1),
#                               options=[{'value': True}],
#                               values=[True],
#                               labelStyle={'display': 'inline-block'},
#                               className='two columns'),
#             ], className='row', id='layer_' + str(n + 1),
#         )
#         div_list.append(current_div)
#     return div_list

# @app.server.route('/plot')
# def build_plot():
#     img = io.BytesIO()
#
#     y = [1, 2, 3, 4, 5]
#     x = [0, 2, 1, 3, 4]
#     plt.plot(x, y)
#     plt.savefig(img, format='png')
#     img.seek(0)
#
#     plot_url = base64.b64encode(img.getvalue()).decode()
#
#     return '<img src="data:image/png;base64,{}">'.format(plot_url)

if __name__ == '__main__':
    app.run_server(debug=True)
