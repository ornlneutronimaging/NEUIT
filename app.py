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

# app_flask = flask.Flask(__name__)
# app_dash = dash.Dash(__name__, server=app_flask, url_base_pathname='/dash_plot')

app = dash.Dash(__name__)
# app_flask = app.server


app.layout = html.Div([
    html.Button('Click Me', id='button'),
    html.H3(id='button-clicks'),

    html.Hr(),

    html.Label('Energy min. (eV)'),
    dcc.Input(id='e_min', value=1, type='number', min=0.000001),

    html.Label('Energy max. (eV)'),
    dcc.Input(id='e_max', value=300, type='number', min='e_min', max=10000000),

    html.Label('Energy step (eV)'),
    dcc.Input(id='e_step', value=0.1, type='number', min=0.0001),

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
    html.Hr(),

    html.Div(id='stack'),
    html.Hr(),

    # html.Button('Show plot', id='button-3'),
    # html.Hr(),
    html.Div([
        dcc.Slider(
            id='e_step_slider',
            min=0.0001,
            max=1,
            value=0.01,
            dots=False,
            step=0.0001,
            updatemode='drag',
            marks={i: '{}'.format(10 ** i) for i in range(5)},
        ),
        html.Div(id='e_step_slider_container', style={'margin-top': 20}),

        #
        dcc.RangeSlider(id='e_range_slider',
                        min=0,
                        max=5,
                        value=[1, 2],
                        allowCross=False,
                        dots=False,
                        step=0.01,
                        marks={i: '{}'.format(10 ** i) for i in range(5)},
                        updatemode='drag'
                        ),
        html.Div(id='e_range_slider_container', style={'margin-top': 20}),
    ]),

    dcc.Graph(id='plot'),
])


def transform_value(value):
    return 10 ** value


@app.callback(
    Output('e_step_slider_container', 'children'),
    [Input('e_step_slider', 'value')])
def update_output(value):
    transformed_value = transform_value(value)
    return 'Linear Value: {}, Log Value: [{:0.2f}]'.format(
        str(value),
        transformed_value,
        # transformed_value[
    )


@app.callback(
    Output('e_range_slider_container', 'children'),
    [Input('e_range_slider', 'value')])
def update_output(value):
    transformed_value = [transform_value(v) for v in value]
    return 'Linear Value: {}, Log Value: [{:0.2f}, {:0.2f}]'.format(
        str(value),
        transformed_value[0],
        transformed_value[1]
    )


@app.callback(
    Output('button-clicks', 'children'),
    [Input('button', 'n_clicks')],
)
def clicks(n_clicks):
    return 'Button has been clicked {} times'.format(n_clicks)


@app.callback(
    Output('stack', 'children'),
    [Input('button-2', 'n_clicks'),
     Input('e_min', 'value'),
     Input('e_max', 'value'),
     Input('e_step', 'value'),
     Input('formula', 'value'),
     Input('thickness', 'value'),
     Input('density', 'value')])
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
        return '{}\nStack: {}\nLayer: {}\nelement: {}\n'.format(n_clicks, p_stack, layer, elements)
    else:
        return None


@app.callback(
    Output('plot', 'figure'),
    [Input('button-2', 'n_clicks'),
     Input('e_min', 'value'),
     Input('e_max', 'value'),
     Input('e_step', 'value'),
     Input('formula', 'value'),
     Input('thickness', 'value'),
     Input('density', 'value')])
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


# @app.callback(dash.dependencies.Output('page-content', 'children'),
#               [dash.dependencies.Input('url', 'pathname')])
# def display_page(pathname):
#     return html.Div([
#         html.H3('You are on page {}'.format(pathname)),
#         html.Div(children='''
#                 A web application framework for Python.
#             '''),
#
#         dcc.Graph(
#             id='example-graph',
#             figure={
#                 'data': [
#                     {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
#                     {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
#                 ],
#                 'layout': {
#                     'title': 'Dash Data Visualization'
#                 }
#             }
#         )
#     ])


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
