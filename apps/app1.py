import os
import pprint

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
from ImagingReso.resonance import Resonance
from dash.dependencies import Input, Output, State
from scipy.interpolate import interp1d

from _utilities import init_reso, load_beam_shape, unpack_tb_df_and_add_layer
from app import app

energy_name = 'Energy (eV)'
wave_name = 'Wavelength (\u212B)'
tof_name = 'Time-of-flight (\u03BCs)'
chem_name = 'Chemical formula'
thick_name = 'Thickness (mm)'
density_name = 'Density (g/cm^3)'
ele_name = 'Element'

df_sample = pd.DataFrame({
    chem_name: ['H2O'],
    thick_name: ['2'],
    density_name: ['1'],
})

col_3 = 'three columns'
col_6 = 'six columns'

# Create app layout
layout = html.Div(
    [
        dcc.Link('Home', href='/'),
        html.Br(),
        dcc.Link('Neutron resonance', href='/apps/venus'),
        html.H1('Cold neutron transmission'),
        html.H3('Sample info'),

        # Sample input
        html.Div(
            [
                html.Div(
                    [
                        html.Button('+', id='app1_button_add'),
                        html.Button('-', id='app1_button_del'),
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
                    id='app1_sample_table'
                ),
                dcc.Markdown(
                    '''NOTE: density input can be omitted (leave as blank) only if the input formula is single element, density available [here](http://periodictable.com/Properties/A/Density.al.html) will be used.'''),
                html.Button('Submit', id='app1_button_submit'),
            ]
        ),

        # Transmission at CG-1D
        html.Div(id='app1_result'),
        # Stack display
        html.Div(
            [
                html.Div(id='app1_stack'),
            ],
        ),
    ]
)


@app.callback(
    Output('app1_sample_table', 'rows'),
    [
        Input('app1_button_add', 'n_clicks'),
        Input('app1_button_del', 'n_clicks'),
    ],
    [
        State('app1_sample_table', 'rows'),
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
    Output('app1_result', 'children'),
    [
        Input('app1_button_submit', 'n_clicks'),
    ],
    [
        State('app1_sample_table', 'rows'),
    ])
def calculate_transmission_cg1d(n_clicks, sample_tb_rows):
    _main_path = os.path.abspath(os.path.dirname(__file__))
    _path_to_beam_shape = os.path.join(_main_path, 'instrument_file/beam_shape_cg1d.txt')
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
        return html.Div(
            [
                html.Hr(),
                html.H3('Result'),
                html.H5('Sample transmission:'),
                html.P('The total neutron transmission at CG-1D (ORNL): {} %'.format(total_trans)),
            ]
        )


@app.callback(
    Output('app1_stack', 'children'),
    [
        Input('app1_button_submit', 'n_clicks'),
    ],
    [
        State('app1_sample_table', 'rows'),
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
        div_list = []
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
            div_list.append(html.Br())
        return html.Div([html.H5('Sample stack:'), html.Div(div_list)])
