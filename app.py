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

# Setup app
server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')

app = dash.Dash(__name__)
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

E_MIN = 1e-5
E_MAX = 1e5
E_STEP = 0.01
E_STEP_MIN = 0.001
E_STEP_MAX = 1

# Create app layout
app.layout = html.Div(
    [
        # html.Button('Click Me', id='button'),
        html.H1('ImagingReso'),
        html.Hr(),

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label('Energy min. (eV)'),
                                dcc.Input(id='e_min', type='number', value=1, min=0),
                            ],
                            className='four columns'
                        ),

                        html.Div(
                            [
                                html.Label('Energy max. (eV)'),
                                dcc.Input(id='e_max', type='number', value=100, min=0, max=1e5),
                            ],
                            className='four columns'
                        ),
                        # html.Div(
                        #     [
                        #         dcc.RangeSlider(
                        #             id='e_range_slider',
                        #             min=-5,
                        #             max=5,
                        #             value=[0, 2],
                        #             allowCross=False,
                        #             dots=False,
                        #             step=0.01,
                        #             # updatemode='drag'
                        #             marks={i: '{} eV'.format(10 ** i) for i in range(-5, 6, 1)}),
                        #     ], className='six columns'
                        # ),

                    ],
                    className='row'
                ),

                html.Div(
                    [
                        html.Div(
                            [
                                dcc.RangeSlider(
                                    id='e_range_slider',
                                    min=-5,
                                    max=5,
                                    value=[0, 2],
                                    allowCross=False,
                                    dots=False,
                                    step=0.01,
                                    # updatemode='drag'
                                    marks={i: '{} eV'.format(10 ** i) for i in range(-5, 6, 1)},
                                    # className='nine columns'
                                ),
                                html.Br(),
                            ],
                        ),
                    ], className='row'
                ),

                html.Div(
                    [
                        html.Label('Energy step (eV)'),
                        dcc.Input(id='e_step', type='number', value=0.01, min=0.001, max=1),
                    ], className='row'
                ),

                html.Div(
                    [
                        # html.Div(id='e_range_slider_container', style={'margin-top': 20}),

                        # dcc.RangeSlider(id='e_range_slider',
                        #                 min=-5,
                        #                 max=5,
                        #                 value=[0, 2],
                        #                 allowCross=False,
                        #                 dots=False,
                        #                 step=0.01,
                        #                 marks={i: '{} eV'.format(10 ** i) for i in range(-5, 6, 1)},
                        #                 # updatemode='drag'
                        #                 ),

                        # html.Div(id='e_step_slider_container', style={'margin-top': 20}),
                        dcc.Slider(
                            id='e_step_slider',
                            min=-3,
                            max=0,
                            value=-2,
                            dots=False,
                            step=0.005,
                            # updatemode='drag',
                            marks={i: '{} eV'.format(10 ** i) for i in range(-3, 1, 1)},
                        ),
                    ],
                    className='row'
                ),
            ],
            className='row'
        ),

        html.Hr(),
        html.Div(
            [
                html.Label('Chemical formula'),
                dcc.Input(id='formula', value='Ag', type='text', minlength=1),

                html.Label('Thickness (mm)'),
                dcc.Input(id='thickness', value=0.5, type='number', min=1e-9),

                html.Label('Density (g/cm3) *Input is optional for solid single element layer'),
                dcc.Input(id='density', value=None, type='number', min=1e-9, placeholder='Optional'),
            ]
        ),
        # html.Label('Slider 1'),
        # dcc.Slider(id='slider-1'),
        html.Div(
            [
                dcc.RadioItems(id='y_type',
                               options=[
                                   {'label': 'Attenuation', 'value': 'attenuation'},
                                   {'label': 'Transmission', 'value': 'transmission'},
                                   {'label': 'Total cross-section', 'value': 'sigma'}
                               ],
                               value='attenuation',
                               labelStyle={'display': 'inline-block'}
                               )
            ]
        ),
        html.Div(
            [
                dcc.RadioItems(id='x_type',
                               options=[
                                   {'label': 'Energy', 'value': 'energy'},
                                   {'label': 'Wavelength', 'value': 'lambda'},
                                   {'label': 'Time', 'value': 'time'},
                                   # {'label': 'Total cross-section', 'value': 'time'}
                               ],
                               value='energy',
                               labelStyle={'display': 'inline-block'}
                               )
            ]
        ),
        html.Div(
            [
                dcc.RadioItems(id='time_unit',
                               options=[
                                   {'label': 's', 'value': 's'},
                                   {'label': 'us', 'value': 'us'},
                                   {'label': 'ns', 'value': 'ns'},
                               ],
                               value='us',
                               labelStyle={'display': 'inline-block'}
                               )
            ]
        ),
        html.Div(
            [
                dcc.Checklist(id='log_scale',
                              options=[
                                  {'label': 'x in log', 'value': 'logx'},
                                  {'label': 'y in log', 'value': 'logy'},
                                  {'label': 'None', 'value': 'none'}
                              ],
                              values=['none'],
                              labelStyle={'display': 'inline-block'}
                              )
            ]
        ),

        html.Div(
            [
                html.Button('Submit', id='button_submit'),
            ]
        ),

        # html.Button('Show plot', id='button-3'),
        # html.Hr(),
        # html.Div(id='plot'),
        #
        dcc.Graph(id='plot'),
        html.Div(id='result'),
        html.Hr(),

        html.Div(
            [
                html.Div(id='stack'),
            ],
        ),
        html.Hr(),

    ], className='ten columns offset-by-one')


def transform_value(value):
    return 10 ** value


@app.callback(
    Output('e_step', 'value'),
    [
        Input('e_step_slider', 'value'),
    ])
def update_e_step_from_slider(e_step_slider_value):
    transformed_value = transform_value(e_step_slider_value)
    return transformed_value


@app.callback(
    Output('e_min', 'value'),
    [
        Input('e_range_slider', 'value'),
        # Input('e_min', 'value'),
    ])
def update_e_min_from_slider(e_range_slider_value):
    transformed_value = [transform_value(v) for v in e_range_slider_value]
    return transformed_value[0]


@app.callback(
    Output('e_max', 'value'),
    [
        Input('e_range_slider', 'value'),
        # Input('e_max', 'value'),
    ])
def update_e_max_from_slider(e_range_slider_value):
    transformed_value = [transform_value(v) for v in e_range_slider_value]
    return transformed_value[1]


# @app.callback(
#     Output('e_step', 'value'),
#     [
#         Input('e_step_slider', 'value'),
#         Input('e_step', 'value'),
#
#     ])
# def update_e_step_from_slider(e_step_slider_value, e_step):
#     transformed_value = transform_value(e_step_slider_value)
#     if e_step != transformed_value:
#         return transformed_value
#     else:
#         return e_step
#
#
# @app.callback(
#     Output('e_min', 'value'),
#     [
#         Input('e_range_slider', 'value'),
#         Input('e_min', 'value'),
#     ])
# def update_e_min_from_slider(e_range_slider_value, e_min):
#     transformed_value = [transform_value(v) for v in e_range_slider_value]
#     if e_min != transformed_value[0]:
#         return transformed_value[0]
#     else:
#         return e_min
#
#
# @app.callback(
#     Output('e_max', 'value'),
#     [
#         Input('e_range_slider', 'value'),
#         Input('e_max', 'value'),
#     ])
# def update_e_max_from_slider(e_range_slider_value, e_max):
#     transformed_value = [transform_value(v) for v in e_range_slider_value]
#     if e_max != transformed_value[1]:
#         return transformed_value[1]
#     else:
#         return e_max


# @app.callback(
#     Output('e_step_slider', 'value'),
#     [
#         Input('e_step_slider', 'value'),
#         Input('e_step', 'value'),
#     ])
# def update_slider_from_e_step(e_step_slider_value, e_step):
#     transformed_value = transform_value(e_step_slider_value)
#     if e_step != transformed_value:
#         return transformed_value
#     else:
#         return e_step


# @app.callback(
#     Output('e_step_slider_container', 'children'),
#     [
#         Input('e_step_slider', 'value'),
#     ])
# def update_output(value):
#     transformed_value = transform_value(value)
#     return [
#         html.P('Energy step: {:0.6f} eV'.format(transformed_value)),
#
#     ]
#
#
# @app.callback(
#     Output('e_range_slider_container', 'children'),
#     [
#         Input('e_range_slider', 'value'),
#     ])
# def update_output(value):
#     transformed_value = [transform_value(v) for v in value]
#     return [
#         html.P('Energy Min.: {:0.6f} eV'.format(transformed_value[0])),
#         html.P('Energy Max.: {:0.6f} eV'.format(transformed_value[1])),
#     ]


@app.callback(
    Output('stack', 'children'),
    [
        Input('button_submit', 'n_clicks'),
    ],
    [
        State('e_min', 'value'),
        State('e_max', 'value'),
        State('e_step', 'value'),
        State('formula', 'value'),
        State('thickness', 'value'),
        State('density', 'value'),
    ])
def compute(n_clicks, e_min, e_max, e_step, formula, thickness, density):
    # if n_clicks is not None:
    o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
    if density is not None:
        o_reso.add_layer(formula=formula,
                         thickness=thickness,
                         density=density)
    else:
        o_reso.add_layer(formula=formula,
                         thickness=thickness)
    stack = o_reso.stack
    p_stack = pprint.pformat(o_reso.stack)
    layer = list(stack.keys())
    for each_layer in stack.keys():
        current_layer = stack[each_layer]
        elements = current_layer['elements']
    return [
        html.P("Stack: {}".format(p_stack)),
        html.P("Layer: {}".format(layer)),
        html.P("Element: {}".format(elements)),
        html.P("Clicks: {}".format(n_clicks)),
        html.P("e_min_slider: {}".format(e_min)),
        html.P("e_max_slider: {}".format(e_max)),
        html.P("e_step_slider: {}".format(e_step)),
    ]


# else:
#     return None


@app.callback(
    Output('plot', 'figure'),
    [
        Input('button_submit', 'n_clicks'),
    ],
    [
        State('e_min', 'value'),
        State('e_max', 'value'),
        State('e_step', 'value'),
        State('formula', 'value'),
        State('thickness', 'value'),
        State('density', 'value'),
        State('y_type', 'value'),
        State('x_type', 'value'),
        State('time_unit', 'value'),
    ])
def plot(n_clicks, e_min, e_max, e_step, formula, thickness, density, y_type, x_type, time_unit):
    o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
    if density is not None:
        o_reso.add_layer(formula=formula,
                         thickness=thickness,
                         density=density)
    else:
        o_reso.add_layer(formula=formula,
                         thickness=thickness)
    plotly_fig = o_reso.plot(plotly=True, y_axis=y_type, x_axis=x_type, time_unit=time_unit, all_elements=True,
                             all_isotopes=True)
    plotly_fig.layout.showlegend = True
    return plotly_fig


# def plot(n_clicks, e_min, e_max, e_step, formula, thickness, density):
#     if n_clicks is not None:
#         o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
#         if density is not None:
#             o_reso.add_layer(formula=formula,
#                              thickness=thickness,
#                              density=density)
#         else:
#             o_reso.add_layer(formula=formula,
#                              thickness=thickness)
#         plotly_fig = o_reso.plot(plotly=True, all_elements=True, all_isotopes=True)
#         plotly_fig.layout.showlegend = True
#         return plotly_fig
#     else:
#         return None


@app.callback(
    Output('result', 'children'),
    [
        Input('button_submit', 'n_clicks'),
    ],
    [
        State('formula', 'value'),
        State('thickness', 'value'),
        State('density', 'value'),
        State('y_type', 'value'),
    ])
def calculate_transmission_cg1d(n_clicks, formula, thickness, density, y_type):
    _main_path = os.path.abspath(os.path.dirname(__file__))
    _path_to_beam_shape = os.path.join(_main_path, 'static/instrument_file/beam_shape_cg1d.txt')
    df = load_beam_shape(_path_to_beam_shape)
    o_reso = init_reso(e_min=0.00025,
                       e_max=0.12525,
                       e_step=0.000625)
    if density is not None:
        o_reso.add_layer(formula=formula,
                         thickness=thickness,
                         density=density)
    else:
        o_reso.add_layer(formula=formula,
                         thickness=thickness)
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
    if y_type == 'transmission':
        return html.P('The total neutron transmission at CG-1D: {} %'.format(total_trans))
    else:
        return html.P('The total neutron attenuation at CG-1D: {} %'.format(100 - total_trans))


# @app.server.route('/reso_plot', methods=['GET', 'POST'])
# def index():
#     init_form = InitForm(request.form)
#     sample_form = SampleForm(request.form)
#     if request.method == 'POST':
#
#         if init_form.validate() and sample_form.validate():
#             o_reso = init_reso(init_form.e_min.data,
#                                init_form.e_max.data,
#                                init_form.e_step.data)
#             o_reso.add_layer(sample_form.formula.data,
#                              sample_form.thickness.data,
#                              sample_form.density.data)
#         result = o_reso.stack
#         plot = o_reso.plot(plotly=True)
#         # pprint.pprint(plot)
#         # app_dash.layout = html.Div(children=[
#         #     html.H1(children='Resonance Plot'),
#         #
#         #     html.Div(children='''
#         #             A web application for resonance imaging.
#         #         '''),
#         #
#         #     dcc.Graph(plot)
#         # ])
#     else:
#         result = None
#         plot = None
#
#     return render_template('view_reso.html',
#                            init_form=init_form,
#                            sample_form=sample_form,
#                            result=result,
#                            plot=plot)

# @app_flask.route('/cg1d', methods=['GET', 'POST'])
# def cg1d():
#     sample_form = SampleForm(request.form)
#     _main_path = os.path.abspath(os.path.dirname(__file__))
#     _path_to_beam_shape = os.path.join(_main_path, 'static/instrument_file/beam_shape_cg1d.txt')
#     df = load_beam_shape(_path_to_beam_shape)
#     if request.method == 'POST' and sample_form.validate():
#         o_reso = init_reso(e_min=0.00025,
#                            e_max=0.12525,
#                            e_step=0.000625)
#         o_reso.add_layer(sample_form.formula.data,
#                          sample_form.thickness.data,
#                          sample_form.density.data)
#         # interpolate with the beam shape energy ()
#         interp_type = 'cubic'
#         energy = o_reso.total_signal['energy_eV']
#         trans = o_reso.total_signal['transmission']
#         interp_function = interp1d(x=energy, y=trans, kind=interp_type)
#         # add interpolated transmission value to beam shape df
#         trans = interp_function(df['energy_eV'])
#         # calculated transmitted flux
#         trans_flux = trans * df['flux']
#         stack = o_reso.stack
#         # stack = pprint.pformat(o_reso.stack)
#
#         _total_trans = sum(trans_flux) / sum(df['flux']) * 100
#         total_trans = round(_total_trans, 3)
#     else:
#         total_trans = None
#         stack = None
#     return render_template('view_cg1d.html',
#                            sample_form=sample_form,
#                            total_trans=total_trans,
#                            stack=stack)
#
#
@app.server.route('/plot')
def build_plot():
    img = io.BytesIO()

    y = [1, 2, 3, 4, 5]
    x = [0, 2, 1, 3, 4]
    plt.plot(x, y)
    plt.savefig(img, format='png')
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()

    return '<img src="data:image/png;base64,{}">'.format(plot_url)


if __name__ == '__main__':
    app.run_server(debug=True)
