import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from ImagingReso._utilities import ev_to_angstroms
from ImagingReso._utilities import ev_to_s
from ImagingReso.resonance import Resonance
from dash.dependencies import Input, Output, State
import dash_table_experiments as dt
from flask import Flask
from scipy.interpolate import interp1d

from compute import init_reso, load_beam_shape, unpack_tb_df_and_add_layer
import pandas as pd
import numpy as np
import pprint

# Setup app
server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')

app = dash.Dash(__name__)
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

energy_name = 'Energy (eV)'
wave_name = 'Wavelength (\u212B)'
tof_name = 'Time-of-flight (\u03BCs)'
chem_name = 'Chemical formula'
thick_name = 'Thickness (mm)'
density_name = 'Density (g/cm^3)'
ele_name = 'Element'

df_range = pd.DataFrame({
    energy_name: [1, 100],
    wave_name: [np.NaN, np.NaN],
    tof_name: [np.NaN, np.NaN],
})

df_sample = pd.DataFrame({
    chem_name: ['Ag'],
    thick_name: ['1'],
    density_name: [''],
})

col_3 = 'three columns'
col_6 = 'six columns'
# Create app layout
app.layout = html.Div(
    [
        # Heading section
        html.Div(
            [
                html.H1(
                    children='ImagingReso',
                ),
            ], className="row"
        ),
        html.Div(
            [
                dcc.Markdown('''
A web application for **Neutron Resonance Imaging**.
'''),
                dcc.Markdown('''

*[ImagingReso](http://imagingreso.readthedocs.io/en/latest/)*
is an open-source Python library that simulates the neutron
resonance signal for neutron imaging measurements. By defining the sample
information such as density, thickness in the neutron path, and isotopic
ratios of the elemental composition of the material, this package plots
the expected resonance peaks for a selected neutron energy range.

The energy dependent cross-section data used in this library are from
[National Nuclear Data Center](http://www.nndc.bnl.gov/), a published
online database. [Evaluated Nuclear Data File](http://www.nndc.bnl.gov/exfor/endf00.jsp)
([ENDF/B-VII.1](https://www.sciencedirect.com/science/article/pii/S009037521100113X)) 
is currently supported and more evaluated databases will be added in the future.
'''),
            ],
        ),
        html.H3('Global parameters'),
        # Global parameters
        html.Div(
            [
                # Range input
                html.H6('Energy slider:'),
                html.Div(
                    [
                        # Energy slider
                        dcc.RangeSlider(
                            id='e_range_slider',
                            min=-5,
                            max=6,
                            value=[0, 2],
                            allowCross=False,
                            dots=False,
                            step=0.01,
                            updatemode='drag',
                            marks={i: '{} eV'.format(pow(10, i)) for i in range(-5, 7, 1)},
                            className='ten columns offset-by-one',
                        ),
                    ], className='row'
                ),
                html.Br(),
                html.Br(),
                html.H6('Range selected:'),
                html.Div([
                    dt.DataTable(
                        rows=df_range.to_dict('records'),
                        # optional - sets the order of columns
                        columns=df_range.columns,
                        # sortColumn=False,
                        editable=False,
                        row_selectable=False,
                        filterable=False,
                        sortable=True,
                        id='range_table'
                    ),
                ]),

                html.Div(
                    [
                        html.Br(),
                        dcc.Markdown('''Source-to-detector (m)'''),
                        dcc.Input(id='distance', type='number', value=16.45, min=1,
                                  inputmode='numeric',
                                  step=0.01,
                                  ),
                        dcc.Markdown(
                            '''NOTE: Please ignore the above input field if **NOT** interested in display of time-of-flight (TOF).'''),
                    ], className='row',
                ),

                # Step input
                html.H6('Energy step:'),
                html.Div(
                    [
                        dcc.Dropdown(
                            id='e_step',
                            options=[
                                {'label': '0.001 (eV)', 'value': 0.001},
                                {'label': '0.01 (eV)', 'value': 0.01},
                                {'label': '0.1 (eV)', 'value': 0.1},
                                {'label': '1 (eV)', 'value': 1},
                                {'label': '10 (eV)', 'value': 10},
                                {'label': '100 (eV)', 'value': 100},
                            ],
                            value=0.01,
                            searchable=False,
                            clearable=False,
                            className='three columns',
                        ),
                    ], className='row'
                ),
                dcc.Markdown('''NOTE: Pick a suitable energy step base on the energy range selected.'''),
            ]
        ),
        html.H3('Sample info'),

        # Sample input
        html.Div([
            html.Div(
                [
                    html.Button('+', id='button_add'),
                    html.Button('-', id='button_del'),
                ], className='row'
            ),

            dt.DataTable(
                rows=df_sample.to_dict('records'),
                # optional - sets the order of columns
                columns=df_sample.columns,
                editable=True,
                row_selectable=False,
                filterable=False,
                sortable=False,
                id='sample_table'
            ),
            dcc.Markdown(
                '''NOTE: density input can be omitted (leave as blank) only if the input formula is single element, density available [here](http://periodictable.com/Properties/A/Density.al.html) will be used.'''),
            html.Button('Submit', id='button_submit'),
        ]
        ),

        html.Hr(),
        # Transmission at CG-1D
        html.Div(id='result'),
        # Plot control buttons
        html.Div(
            [
                html.H5('Plot options:'),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P('X options: '),
                                dcc.RadioItems(id='x_type',
                                               options=[
                                                   {'label': 'Energy (eV)', 'value': 'energy'},
                                                   {'label': 'Wavelength (\u212B)', 'value': 'lambda'},
                                                   {'label': 'Time-of-flight (\u03BCs)', 'value': 'time'},
                                               ],
                                               value='energy',
                                               )
                            ], className=col_3
                        ),
                        html.Div(
                            [
                                html.P('Y options: '),
                                dcc.RadioItems(id='y_type',
                                               options=[
                                                   {'label': 'Attenuation', 'value': 'attenuation'},
                                                   {'label': 'Transmission', 'value': 'transmission'},
                                                   {'label': 'Total cross-section (barn)', 'value': 'sigma'}
                                               ],
                                               value='attenuation',
                                               )
                            ], className=col_3
                        ),
                        html.Div(
                            [
                                html.P('Scale options: '),
                                dcc.RadioItems(id='plot_scale',
                                               options=[
                                                   {'label': 'Linear', 'value': 'linear'},
                                                   {'label': 'Log x', 'value': 'logx'},
                                                   {'label': 'Log y', 'value': 'logy'},
                                                   {'label': 'Loglog', 'value': 'loglog'},
                                               ],
                                               value='linear',
                                               )
                            ], className=col_3
                        ),
                        html.Div(
                            [
                                html.P('Show options: '),
                                dcc.Checklist(id='show_opt',
                                              options=[
                                                  {'label': 'Total', 'value': 'total'},
                                                  {'label': 'Layer', 'value': 'layer'},
                                                  {'label': 'Element', 'value': 'ele'},
                                                  {'label': 'Isotope', 'value': 'iso'},
                                              ], values=['ele'],
                                              ),
                            ], className=col_3
                        ),
                    ], className='row'
                ),
                # Plot
                html.Div(id='plot'),
                html.Button('Export to clipboard', id='button_export'),
                html.Div(id='export_done'),
            ]
        ),

        # Stack display
        html.Hr(),
        html.Div(
            [
                html.Div(id='stack'),
            ],
        ),
        dcc.Markdown('''
#### Publication
 
Yuxuan Zhang and Jean Bilheux, (2017), ImagingReso: A Tool for Neutron Resonance Imaging, Journal of Open Source Software, 2(19), 407,
[doi:10.21105/joss.00407](http://joss.theoj.org/papers/997d09281a9d76e95f4ec4d3279eeb8c)
'''),
    ], className='ten columns offset-by-one'
)


@app.callback(
    Output('range_table', 'rows'),
    [
        Input('e_range_slider', 'value'),
        Input('distance', 'value'),
    ]
)
def show_range_table(slider, distance):
    transformed_value = [pow(10, v) for v in slider]
    e_min = round(transformed_value[0], 5)
    e_max = round(transformed_value[1], 5)
    lambda_1 = round(ev_to_angstroms(array=e_min), 4)
    lambda_2 = round(ev_to_angstroms(array=e_max), 4)
    tof_1 = round(ev_to_s(array=e_min, source_to_detector_m=distance, offset_us=0) * 1e6, 4)
    tof_2 = round(ev_to_s(array=e_max, source_to_detector_m=distance, offset_us=0) * 1e6, 4)
    _df_range = pd.DataFrame({
        energy_name: [e_min, e_max],
        wave_name: [lambda_1, lambda_2],
        tof_name: [tof_1, tof_2],
    })
    return _df_range.to_dict('records')


@app.callback(
    Output('sample_table', 'rows'),
    [
        Input('button_add', 'n_clicks'),
        Input('button_del', 'n_clicks'),
    ],
    [
        State('sample_table', 'rows'),
    ])
def add_del_row(n_add, n_del, sample_tb_rows):
    if n_add is None:
        n_add = 0
    if n_del is None:
        n_del = 0
    df_sample_tb = pd.DataFrame(sample_tb_rows)
    if chem_name not in df_sample_tb.columns:
        df_sample_tb[chem_name] = ['']
    if thick_name not in df_sample_tb.columns:
        df_sample_tb[thick_name] = ['']
    if density_name not in df_sample_tb.columns:
        df_sample_tb[density_name] = ['']
    n_layer = len(df_sample_tb[chem_name])
    _formula_list = list(df_sample_tb[chem_name])
    _thickness_list = list(df_sample_tb[thick_name])
    _density_list = list(df_sample_tb[density_name])
    n_row = n_add - n_del + 1
    if n_row > n_layer:
        _formula_list.append('')
        _thickness_list.append('')
        _density_list.append('')
    elif n_row < n_layer:
        _formula_list.pop()
        _thickness_list.pop()
        _density_list.pop()
    _df_sample = pd.DataFrame({
        chem_name: _formula_list,
        thick_name: _thickness_list,
        density_name: _density_list,
    })
    return _df_sample.to_dict('records')


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


@app.callback(
    Output('plot', 'children'),
    [
        Input('button_submit', 'n_clicks'),
        Input('y_type', 'value'),
        Input('x_type', 'value'),
        Input('plot_scale', 'value'),
        Input('show_opt', 'values'),
    ],
    [
        State('range_table', 'rows'),
        State('e_step', 'value'),
        State('distance', 'value'),
        State('sample_table', 'rows'),
    ])
def plot(n_submit, y_type, x_type, plot_scale, show_opt,
         range_tb_rows, e_step, distance_m,
         sample_tb_rows,
         ):
    if n_submit is not None:

        df_range_tb = pd.DataFrame(range_tb_rows)
        e_min = df_range_tb['Energy (eV)'][0]
        e_max = df_range_tb['Energy (eV)'][1]
        o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
        df_sample_tb = pd.DataFrame(sample_tb_rows)
        o_reso = unpack_tb_df_and_add_layer(o_reso=o_reso,
                                            sample_tb_df=df_sample_tb)
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
        show_total = False
        show_layer = False
        show_ele = False
        show_iso = False
        if 'total' in show_opt:
            show_total = True
        if 'layer' in show_opt:
            show_layer = True
        if 'ele' in show_opt:
            show_ele = True
        if 'iso' in show_opt:
            show_iso = True
        plotly_fig = o_reso.plot(plotly=True,
                                 y_axis=y_type,
                                 x_axis=x_type,
                                 time_unit='us',
                                 logy=_log_y,
                                 logx=_log_x,
                                 mixed=show_total,
                                 all_layers=show_layer,
                                 all_elements=show_ele,
                                 all_isotopes=show_iso,
                                 source_to_detector_m=distance_m)
        plotly_fig.layout.showlegend = True
        return html.Div(
            [
                dcc.Graph(id='reso_plot', figure=plotly_fig)
            ]
        )


@app.callback(
    Output('export_done', 'children'),
    [
        Input('button_export', 'n_clicks'),
    ],
    [
        State('y_type', 'value'),
        State('x_type', 'value'),
        State('show_opt', 'values'),
        State('range_table', 'rows'),
        State('e_step', 'value'),
        State('distance', 'value'),
        State('sample_table', 'rows'),
    ])
def export(n_export_to_clipboard,
           y_type, x_type, show_opt,
           range_tb_rows, e_step, distance_m,
           sample_tb_rows
           ):
    df_range_tb = pd.DataFrame(range_tb_rows)
    e_min = df_range_tb[energy_name][0]
    e_max = df_range_tb[energy_name][1]
    o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
    df_sample_tb = pd.DataFrame(sample_tb_rows)
    o_reso = unpack_tb_df_and_add_layer(o_reso=o_reso,
                                        sample_tb_df=df_sample_tb)

    show_total = False
    show_layer = False
    show_ele = False
    show_iso = False
    if 'total' in show_opt:
        show_total = True
    if 'layer' in show_opt:
        show_layer = True
    if 'ele' in show_opt:
        show_ele = True
    if 'iso' in show_opt:
        show_iso = True

    if n_export_to_clipboard is not None:
        o_reso.export(y_axis=y_type,
                      x_axis=x_type,
                      time_unit='us',
                      mixed=show_total,
                      all_layers=show_layer,
                      all_elements=show_ele,
                      all_isotopes=show_iso,
                      source_to_detector_m=distance_m)
        return html.P('Data copied.', style={'marginBottom': 10, 'marginTop': 5})


@app.callback(
    Output('result', 'children'),
    [
        Input('button_submit', 'n_clicks'),
    ],
    [
        State('y_type', 'value'),
        State('sample_table', 'rows'),
    ])
def calculate_transmission_cg1d(n_clicks, y_type, sample_tb_rows):
    _main_path = os.path.abspath(os.path.dirname(__file__))
    _path_to_beam_shape = os.path.join(_main_path, 'static/instrument_file/beam_shape_cg1d.txt')
    df = load_beam_shape(_path_to_beam_shape)
    o_reso = init_reso(e_min=0.00025,
                       e_max=0.12525,
                       e_step=0.000625)
    df_sample_tb = pd.DataFrame(sample_tb_rows)
    o_reso = unpack_tb_df_and_add_layer(o_reso=o_reso,
                                        sample_tb_df=df_sample_tb)
    # interpolate with the beam shape energy ()
    interp_type = 'cubic'
    energy = o_reso.total_signal['energy_eV']
    trans = o_reso.total_signal['transmission']
    interp_function = interp1d(x=energy, y=trans, kind=interp_type)
    # add interpolated transmission value to beam shape df
    trans = interp_function(df['energy_eV'])
    # calculated transmitted flux
    trans_flux = trans * df['flux']
    _total_trans = sum(trans_flux) / sum(df['flux']) * 100
    total_trans = round(_total_trans, 3)
    if n_clicks is not None:
        if y_type == 'transmission':
            return html.Div(
                [
                    html.H3('Result'),
                    html.H5('Sample transmission:'),
                    html.P('The total neutron transmission at CG-1D (ORNL): {} %'.format(total_trans)),
                    html.Hr()
                ]
            )
        else:
            return html.Div(
                [
                    html.H3('Result'),
                    html.H5('Sample attenuation:'),
                    html.P('The total neutron attenuation at CG-1D (ORNL): {} %'.format(100 - total_trans)),
                    html.Hr()
                ]
            )


@app.callback(
    Output('stack', 'children'),
    [
        Input('button_submit', 'n_clicks'),
    ],
    [
        State('sample_table', 'rows'),
    ])
def show_stack(n_clicks, sample_tb_rows):
    if n_clicks is not None:
        o_reso = Resonance(energy_min=1, energy_max=2, energy_step=1)
        df_sample_tb = pd.DataFrame(sample_tb_rows)
        o_reso = unpack_tb_df_and_add_layer(o_reso=o_reso,
                                            sample_tb_df=df_sample_tb)
        o_stack = o_reso.stack
        pprint.pprint(o_stack)
        # stack_str = pprint.pformat(o_stack)
        div_list = [html.H4('Stack info'),
                    # html.P("Stack: {}".format(o_stack)),
                    ]
        layers = list(o_stack.keys())
        layer_dict = {}
        for l, layer in enumerate(layers):
            elements_in_current_layer = o_stack[layer]['elements']
            l_str = str(l + 1)
            current_layer_list = [
                html.P("Layer {}: {}".format(l_str, layer)),
            ]
            # layer_dict['Layer ' + l_str] = layer
            layer_dict[thick_name] = o_stack[layer]['thickness']['value']
            layer_dict[density_name] = o_stack[layer]['density']['value']
            # layer_dict['Elements'] = elements_in_current_layer
            _df_layer = pd.DataFrame([layer_dict])
            current_layer_list.append(
                dt.DataTable(rows=_df_layer.to_dict('records'),
                             # optional - sets the order of columns
                             columns=_df_layer.columns,
                             editable=False,
                             row_selectable=False,
                             filterable=False,
                             sortable=False,
                             # id='sample_table'
                             ))

            for e, ele in enumerate(elements_in_current_layer):
                _iso_list = o_stack[layer][ele]['isotopes']['list']
                _iso_ratios = o_stack[layer][ele]['isotopes']['isotopic_ratio']
                # current_layer_list.append(html.H6("Element: {}".format(ele)))
                # current_layer_list.append(html.P("Isotopes: "))
                # iso_dict = {ele_name: ele}
                iso_dict = {}
                for i, iso in enumerate(_iso_list):
                    iso_dict[iso] = _iso_ratios[i]
                _df_iso = pd.DataFrame([iso_dict])
                current_layer_list.append(
                    dt.DataTable(rows=_df_iso.to_dict('records'),
                                 # optional - sets the order of columns
                                 columns=_df_iso.columns,
                                 editable=False,
                                 row_selectable=False,
                                 filterable=False,
                                 sortable=False,
                                 # id='sample_table'
                                 ))

            div_list.append(html.Div(current_layer_list))
        return div_list


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
