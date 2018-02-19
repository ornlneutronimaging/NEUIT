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

# app.layout = html.Div(children=[
#     html.H1(children='Hello Dash'),
#     html.Div([
#         html.Div(
#             dcc.Input(id='input_formula',
#                       name='formula',
#                       placeholder='Enter chemical formula...',
#                       type='text',
#                       value='',
#                       ),
#             # dcc.Input(id='input_thickness',
#             #           name='thickness',
#             #           placeholder='Enter thickness (mm)...',
#             #           type='number',
#             #           value='',
#             #           ),
#             # dcc.Input(id='input_density',
#             #           name='density',
#             #           placeholder='Enter density (g/cm3)...',
#             #           type='number',
#             #           value='',
#             #           ),
#         ),
#         html.Button('Submit', id='button'),
#         html.Div(id='output-container-button',
#                  children='Enter a value and press submit')
#     ])
#     ,
#     html.Hr(),
#     html.Div(children='''
#             Dash: A web application framework for Python.
#         '''),
#
#     dcc.Graph(
#         id='example-graph',
#         figure={
#             'data': [
#                 {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
#                 {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
#             ],
#             'layout': {
#                 'title': 'Dash Data Visualization'
#             }
#         }
#     )
# ])
# @app.callback(
#     dash.dependencies.Output('output-container-button', 'children'),
#     [dash.dependencies.Input('button', 'n_clicks')],
#     [dash.dependencies.State('input_formula', 'value')])
# def update_output(n_clicks, value):
#     return 'The input value was "{}" and the button has been clicked {} times'.format(
#         value,
#         n_clicks
#     )


# app.layout = html.Div([
#     # represents the URL bar, doesn't render anything
#     dcc.Location(id='url', refresh=False),
#
#     dcc.Link('Navigate to "/"', href='/'),
#     html.Br(),
#     dcc.Link('Navigate to "/page-2"', href='/page-2'),
#     # content will be rendered in this element
#     html.Div(id='page-content'),
#
#     html.Div(
#         dcc.Input(id='input_formula',
#                   name='formula',
#                   placeholder='Enter chemical formula...',
#                   type='text',
#                   value='',
#                   ),
#     ),
#     html.Button('Submit', id='button'),
#     html.Div(id='output-container-button',
#              children='Enter a value and press submit')
# ])
#
#
# @app.callback(
#     dash.dependencies.Output('output-container-button', 'children'),
#     [dash.dependencies.Input('button', 'n_clicks')],
#     [dash.dependencies.State('input_formula', 'value')])
# def update_output(n_clicks, value):
#     return 'The input value was "{}" and the button has been clicked {} times'.format(
#         value,
#         n_clicks
#     )


app.layout = html.Div([
    html.Button('Click Me', id='button'),
    html.H3(id='button-clicks'),

    html.Hr(),

    html.Label('Energy min. (eV)'),
    dcc.Input(id='e_min', value=1),

    html.Label('Energy max. (eV)'),
    dcc.Input(id='e_max', value=300),

    html.Label('Energy step (eV)'),
    dcc.Input(id='e_step', value=0.1),

    html.Hr(),

    html.Label('Chemical formula'),
    dcc.Input(id='formula', value='Ag'),

    html.Label('Thickness (mm)'),
    dcc.Input(id='thickness', value=0.5),

    html.Label('Density (g/cm3)'),
    dcc.Input(id='density', value=2),

    # html.Label('Slider 1'),
    # dcc.Slider(id='slider-1'),
    html.Br(),

    html.Button('Show stack', id='button-2'),

    html.Div(id='output')
])


@app.callback(
    Output('button-clicks', 'children'),
    [Input('button', 'n_clicks')])
def clicks(n_clicks):
    return 'Button has been clicked {} times'.format(n_clicks)


@app.callback(
    Output('output', 'children'),
    [Input('button-2', 'n_clicks')],
    state=[State('e_min', 'value'),
           State('e_max', 'value'),
           State('e_step', 'value'),
           State('formula', 'value'),
           State('thickness', 'value'),
           State('density', 'value')])
def compute(n_clicks, e_min, e_max, e_step, formula, thickness, density):
    o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)

    o_reso.add_layer(formula,
                     thickness,
                     density)
    stack = o_reso.stack
    p_stack = pprint.pformat(o_reso.stack)
    layer = list(stack.keys())
    for each_layer in stack.keys():
        current_layer = stack[each_layer]
        elements = current_layer['elements']
    return 'Stack: {}\nLayer: {}\nelement: {}\n'.format(p_stack, layer, elements)


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
