from model import InitForm
from model import SampleForm
import flask
from flask import render_template, request
from compute import init_reso, add_layer, load_beam_shape
#
import io
import os
import matplotlib.pyplot as plt
import base64
from scipy.interpolate import interp1d
#
#
# app = Flask(__name__)
from ImagingReso.resonance import Resonance
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pprint

app = dash.Dash(__name__)
# app_flask = app.server


app.layout = html.Div(
    [
        html.Button('Click Me', id='button'),
        html.H3(id='button-clicks'),

        html.Hr(),

        html.Label('Energy min. (eV)'),
        dcc.Input(id='e_min', type='number', min=0.000001),

        html.Label('Energy max. (eV)'),
        dcc.Input(id='e_max', type='number', min='e_min', max=10000000),

        html.Label('Energy step (eV)'),
        dcc.Input(id='e_step', type='number', min=0.01),

        html.Hr(),

        html.Label('Chemical formula'),
        dcc.Input(id='formula', value='Ag', type='text', minlength=1),

        html.Label('Thickness (mm)'),
        dcc.Input(id='thickness', value=0.5, type='number', min=0),

        html.Label('Density (g/cm3) *Input is optional for solid single element layer'),
        dcc.Input(id='density', value=None, type='number', min=0, placeholder='Optional'),

        # html.Label('Slider 1'),
        # dcc.Slider(id='slider-1'),
        html.Br(),

        html.Button('Submit', id='button-2'),

        # html.Button('Show plot', id='button-3'),
        # html.Hr(),
        html.Div(
            [
                html.Div(id='e_step_slider_container', style={'margin-top': 20}),

                dcc.Slider(
                    id='e_step_slider',
                    min=-2,
                    max=1,
                    value=-1,
                    dots=False,
                    step=0.005,
                    # updatemode='drag',
                    marks={i: '{}'.format(10 ** i) for i in range(-2, 2, 1)},
                ),

                html.Div(id='e_range_slider_container', style={'margin-top': 20}),

                dcc.RangeSlider(id='e_range_slider',
                                min=-5,
                                max=5,
                                value=[0, 2],
                                allowCross=False,
                                dots=False,
                                step=0.01,
                                marks={i: '{}'.format(10 ** i) for i in range(-5, 5, 1)},
                                # updatemode='drag'
                                ),
            ]),

        # html.Div(id='plot'),
        #
        dcc.Graph(id='plot'),
        html.Hr(),

        html.Div(id='stack'),
        html.Hr(),

    ])


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


@app.callback(
    Output('e_step_slider_container', 'children'),
    [
        Input('e_step_slider', 'value'),
    ])
def update_output(value):
    transformed_value = transform_value(value)
    return [
        html.P('Energy step: {:0.6f} eV'.format(transformed_value)),

    ]


@app.callback(
    Output('e_range_slider_container', 'children'),
    [
        Input('e_range_slider', 'value'),
    ])
def update_output(value):
    transformed_value = [transform_value(v) for v in value]
    return [
        html.P('Energy Min.: {:0.6f} eV'.format(transformed_value[0])),
        html.P('Energy Max.: {:0.6f} eV'.format(transformed_value[1])),
    ]


@app.callback(
    Output('button-clicks', 'children'),
    [Input('button', 'n_clicks')],
)
def clicks(n_clicks):
    return 'Button has been clicked {} times'.format(n_clicks)


@app.callback(
    Output('stack', 'children'),
    [
        Input('button-2', 'n_clicks'),
        Input('e_min', 'value'),
        Input('e_max', 'value'),
        Input('e_step', 'value'),
        Input('formula', 'value'),
        Input('thickness', 'value'),
        Input('density', 'value'),
    ])
def compute(n_clicks, e_min, e_max, e_step, formula, thickness, density):
    if n_clicks is not None:
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
    else:
        return None


# def update_value()


@app.callback(
    Output('plot', 'figure'),
    [
        Input('button-2', 'n_clicks'),
        Input('e_min', 'value'),
        Input('e_max', 'value'),
        Input('e_step', 'value'),
        Input('formula', 'value'),
        Input('thickness', 'value'),
        Input('density', 'value'),
    ])
def plot(n_clicks, e_min, e_max, e_step, formula, thickness, density):
    if n_clicks is not None:
        o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
        if density is not None:
            o_reso.add_layer(formula=formula,
                             thickness=thickness,
                             density=density)
        else:
            o_reso.add_layer(formula=formula,
                             thickness=thickness)
        plotly_fig = o_reso.plot(plotly=True, all_elements=True, all_isotopes=True)
        plotly_fig.layout.showlegend = True
        return plotly_fig
    else:
        return None


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


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
