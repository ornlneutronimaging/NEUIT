import numpy as np
from ImagingReso._utilities import ev_to_angstroms
from ImagingReso._utilities import ev_to_s
from dash.dependencies import Input, Output, State
from _app import app
import urllib.parse
from _utilities import *

energy_range_df_default = pd.DataFrame({
    'column_1': [1, 100],
    'column_2': [np.NaN, np.NaN],
    'column_3': [np.NaN, np.NaN],
})

sample_df_default = pd.DataFrame({
    'column_1': ['Ag'],
    'column_2': ['1'],
    'column_3': [''],
})

plot_data_filename = "plot_data.csv"

# Create app2 layout
layout = html.Div(
    [
        dcc.Link('Home', href='/'),
        html.Br(),
        dcc.Link('Cold neutron transmission', href='/apps/cg1d'),
        html.Br(),
        dcc.Link('Composition converter', href='/apps/converter'),
        html.H1('Neutron resonance'),
        # Global parameters
        html.Div(
            [
                # Range input
                html.H6('Energy range:'),
                html.Div(
                    [
                        # Energy slider
                        dcc.RangeSlider(
                            id='app2_e_range_slider',
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
                html.Div([
                    dt.DataTable(
                        data=energy_range_df_default.to_dict('records'),
                        # optional - sets the order of columns
                        columns=energy_range_header_df.to_dict('records'),
                        editable=False,
                        row_selectable=False,
                        filtering=False,
                        sorting=False,
                        row_deletable=False,
                        id='app2_range_table'
                    ),
                ]),
                html.Div(
                    [
                        # Step input
                        html.Div(
                            [
                                html.H6('Energy step:'),
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            id='app2_e_step',
                                            options=[
                                                {'label': '0.001 (eV)  (NOT recommended if energy range > 10 eV)',
                                                 'value': 0.001},
                                                {'label': '0.01 (eV)', 'value': 0.01},
                                                {'label': '0.1 (eV)', 'value': 0.1},
                                                {'label': '1 (eV)', 'value': 1},
                                                {'label': '10 (eV)', 'value': 10},
                                                {'label': '100 (eV)', 'value': 100},
                                            ],
                                            value=0.01,
                                            searchable=False,
                                            clearable=False,
                                        ),
                                    ]
                                ),
                                dcc.Markdown(
                                    '''NOTE: Pick a suitable energy step base on the energy range selected.'''),
                            ], className='five columns', style={'verticalAlign': 'middle'},
                        ),
                        html.Div(
                            [
                                html.H6('Source-to-detector (optional):'),
                                html.Div(
                                    [
                                        dcc.Input(id='app2_distance', type='number', value=16.45, min=1,
                                                  inputmode='numeric',
                                                  step=0.01,
                                                  className='nine columns'),
                                        html.P('(m)', className='one column',
                                               style={'marginBottom': 10, 'marginTop': 5},
                                               # style={'verticalAlign': 'middle'},
                                               ),
                                    ], className='row', style={'verticalAlign': 'middle'},
                                ),
                                dcc.Markdown(
                                    '''NOTE: Please ignore the above input field if **NOT** 
                                    interested in display of time-of-flight (TOF).'''),
                            ], className=col_width_6,
                        ),
                    ], className='row',
                ),
            ]
        ),

        # Sample input
        html.H3('Sample info'),
        html.Div([
            html.Button('Add Row', id='app2_add_row', n_clicks=0),
            dt.DataTable(
                data=sample_df_default.to_dict('records'),
                # optional - sets the order of columns
                columns=sample_header_df.to_dict('records'),
                editable=True,
                row_selectable=False,
                filtering=False,
                sorting=False,
                row_deletable=True,
                style_cell_conditional=[
                    {'if': {'column_id': column_1},
                     'width': '33%'},
                    {'if': {'column_id': column_2},
                     'width': '33%'},
                    {'if': {'column_id': column_3},
                     'width': '33%'},
                ],
                id='app2_sample_table'
            ),
            markdown_sample,
            dcc.Checklist(id='app2_iso_check',
                          options=[
                              {'label': 'Modify isotopic ratios', 'value': True},
                          ], values=[],
                          ),
            html.Div(
                [
                    markdown_iso,
                    dt.DataTable(
                        data=iso_tb_df_default.to_dict('records'),
                        columns=iso_tb_header_df.to_dict('records'),
                        editable=True,
                        # editable={layer_name: False,
                        #           ele_name: False,
                        #           iso_name: True,
                        #           },
                        row_selectable=False,
                        filtering=False,
                        sorting=False,
                        row_deletable=False,
                        style_cell_conditional=[
                            {'if': {'column_id': column_1},
                             'width': '25%'},
                            {'if': {'column_id': column_2},
                             'width': '25%'},
                            {'if': {'column_id': column_3},
                             'width': '25%'},
                            {'if': {'column_id': column_4},
                             'width': '25%'},
                        ],
                        style_table={
                            'maxHeight': '300',
                            'overflowY': 'scroll'
                        },
                        id='app2_iso_table'
                    ),
                ],
                id='app2_iso_input',
                style={'display': 'none'},
            ),
            html.Button('Submit', id='app2_button_submit'),
        ]
        ),

        # Error message
        html.Div(id='app2_error'),

        # Plot
        html.Div(
            [
                html.Div(id='app2_plot_options', children=plot_option_div),
                html.Div(
                    [
                        dcc.Checklist(id='app2_export_clip',
                                      options=[
                                          {'label': 'Clipboard', 'value': False},
                                      ], values=[],
                                      ),
                        html.A(
                            'Download Plot Data',
                            id='app2_download_link',
                            download=plot_data_filename,
                            href="",
                            target="_blank",
                            style={'display': 'inline-block'},
                        ),
                    ], className='row'
                ),
                html.Div(id='app2_plot'),
            ],
            id='app2_plot_div',
            style={'display': 'none'}
        ),
        # Transmission at CG-1D and sample stack
        html.Div(id='app2_result'),
    ]
)


@app.callback(
    Output('app2_range_table', 'data'),
    [
        Input('app2_e_range_slider', 'value'),
        Input('app2_distance', 'value'),
    ])
def show_range_table(slider, distance):
    transformed_value = [pow(10, v) for v in slider]
    e_min = round(transformed_value[0], 5)
    e_max = round(transformed_value[1], 5)
    lambda_1 = round(ev_to_angstroms(array=e_min), 4)
    lambda_2 = round(ev_to_angstroms(array=e_max), 4)
    tof_1 = round(ev_to_s(array=e_min, source_to_detector_m=distance, offset_us=0) * 1e6, 4)
    tof_2 = round(ev_to_s(array=e_max, source_to_detector_m=distance, offset_us=0) * 1e6, 4)
    v_1 = round(3956. / np.sqrt(81.787 / (e_min * 1000.)), 2)
    v_2 = round(3956. / np.sqrt(81.787 / (e_max * 1000.)), 2)
    class_1 = classify_neutron(e_min)
    class_2 = classify_neutron(e_max)
    _df_range = pd.DataFrame({
        column_1: [e_min, e_max],
        column_2: [lambda_1, lambda_2],
        column_3: [v_1, v_2],
        column_4: [tof_1, tof_2],
        column_5: [class_1, class_2],
    })
    return _df_range.to_dict('records')


@app.callback(
    Output('app2_sample_table', 'data'),
    [Input('app2_add_row', 'n_clicks')],
    [State('app2_sample_table', 'data'),
     State('app2_sample_table', 'columns')])
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@app.callback(
    Output('app2_iso_table', 'data'),
    [
        Input('app2_sample_table', 'data'),
    ])
def update_iso_table(compos_tb_dict):
    compos_tb_df = pd.DataFrame(compos_tb_dict)
    sample_df = creat_sample_df_from_compos_df(compos_tb_df=compos_tb_df)
    iso_df = form_iso_table(sample_df=sample_df)
    return iso_df.to_dict('records')


@app.callback(
    Output('app2_iso_input', 'style'),
    [
        Input('app2_iso_check', 'values'),
    ])
def show_hide_iso_table(iso_changed):
    if iso_changed:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('plot_scale', 'options'),
    [
        Input('y_type', 'value'),
    ])
def enable_logx_when_not_plot_sigma(y_type):
    if y_type[:5] == 'sigma':
        options = [
            {'label': 'Linear', 'value': 'linear'},
            {'label': 'Log x', 'value': 'logx'},
            {'label': 'Log y', 'value': 'logy'},
            {'label': 'Loglog', 'value': 'loglog'},
        ]
    else:
        options = [
            {'label': 'Linear', 'value': 'linear'},
            {'label': 'Log x', 'value': 'logx'},
        ]
    return options


@app.callback(
    Output('show_opt', 'options'),
    [
        Input('y_type', 'value'),
    ])
def disable_total_layer_when_plotting_sigma(y_type):
    if y_type[:5] != 'sigma':
        options = [
            {'label': 'Total', 'value': 'total'},
            {'label': 'Layer', 'value': 'layer'},
            {'label': 'Element', 'value': 'ele'},
            {'label': 'Isotope', 'value': 'iso'},
        ]
    else:
        options = [
            {'label': 'Element', 'value': 'ele'},
            {'label': 'Isotope', 'value': 'iso'},
        ]
    return options


@app.callback(
    Output('app2_plot_div', 'style'),
    [
        Input('app2_button_submit', 'n_clicks'),
    ])
def show_plot_options(n_submit):
    if n_submit is not None:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('app2_plot', 'children'),
    [
        Input('app2_button_submit', 'n_clicks'),
        Input('y_type', 'value'),
        Input('x_type', 'value'),
        Input('plot_scale', 'value'),
        Input('show_opt', 'values'),
    ],
    [
        State('app2_range_table', 'data'),
        State('app2_e_step', 'value'),
        State('app2_distance', 'value'),
        State('app2_sample_table', 'data'),
        State('app2_iso_table', 'data'),
        State('app2_iso_check', 'values'),
    ])
def plot(n_submit, y_type, x_type, plot_scale, show_opt,
         range_tb_rows, e_step, distance_m,
         sample_tb_rows, iso_tb_rows,
         iso_changed):
    if n_submit is not None:
        # Modify input for testing
        sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
        iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
        sample_tb_df = pd.DataFrame(sample_tb_dict)
        iso_tb_df = pd.DataFrame(iso_tb_dict)

        # Test input format
        test_passed_list, output_div_list = validate_sample_input(sample_df=sample_tb_df,
                                                                  iso_df=iso_tb_df,
                                                                  sample_schema=sample_dict_schema,
                                                                  iso_schema=iso_dict_schema)

        # Calculation starts
        if all(test_passed_list):
            range_tb_df = pd.DataFrame(range_tb_rows)
            o_reso = init_reso_from_tb(range_tb_df=range_tb_df, e_step=e_step)
            o_reso = unpack_sample_tb_df_and_add_layer(o_reso=o_reso, sample_tb_df=sample_tb_df)
            o_reso = unpack_iso_tb_df_and_update(o_reso=o_reso, iso_tb_df=iso_tb_df, iso_changed=iso_changed)

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
            plotly_fig.layout.autosize = True
            plotly_fig.layout.height = 600
            plotly_fig.layout.width = 900
            plotly_fig.layout.margin = {'b': 52, 'l': 80, 'pad': 0, 'r': 15, 't': 15}
            plotly_fig.layout.xaxis1.tickfont.size = 15
            plotly_fig.layout.xaxis1.titlefont.size = 18
            plotly_fig.layout.yaxis1.tickfont.size = 15
            plotly_fig.layout.yaxis1.titlefont.size = 18

            return html.Div(
                [
                    dcc.Graph(id='app2_reso_plot', figure=plotly_fig, className='container'),
                ]
            )
        else:
            return None


@app.callback(
    Output('app2_download_link', 'href'),
    [
        Input('app2_button_submit', 'n_clicks'),
        Input('y_type', 'value'),
        Input('x_type', 'value'),
        Input('show_opt', 'values'),
        Input('app2_export_clip', 'values'),
    ],
    [
        State('app2_range_table', 'data'),
        State('app2_e_step', 'value'),
        State('app2_distance', 'value'),
        State('app2_sample_table', 'data'),
        State('app2_iso_table', 'data'),
        State('app2_iso_check', 'values'),
    ])
def export_plot_data(n_submit,
                     y_type, x_type, show_opt, export_clip,
                     range_tb_rows, e_step, distance_m,
                     sample_tb_rows, iso_tb_rows,
                     iso_changed):
    if n_submit is not None:
        # Modify input for testing
        sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
        iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
        sample_tb_df = pd.DataFrame(sample_tb_dict)
        iso_tb_df = pd.DataFrame(iso_tb_dict)

        # Test input format
        test_passed_list, output_div_list = validate_sample_input(sample_df=sample_tb_df,
                                                                  iso_df=iso_tb_df,
                                                                  sample_schema=sample_dict_schema,
                                                                  iso_schema=iso_dict_schema)

        # Calculation starts
        if all(test_passed_list):
            range_tb_df = pd.DataFrame(range_tb_rows)
            o_reso = init_reso_from_tb(range_tb_df=range_tb_df, e_step=e_step)
            o_reso = unpack_sample_tb_df_and_add_layer(o_reso=o_reso, sample_tb_df=sample_tb_df)
            o_reso = unpack_iso_tb_df_and_update(o_reso=o_reso, iso_tb_df=iso_tb_df, iso_changed=iso_changed)

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
            if export_clip:
                _type = 'clip'
            else:
                _type = 'df'

            # if n_link_click is not None:
            df = o_reso.export(y_axis=y_type,
                               x_axis=x_type,
                               time_unit='us',
                               mixed=show_total,
                               all_layers=show_layer,
                               all_elements=show_ele,
                               all_isotopes=show_iso,
                               source_to_detector_m=distance_m,
                               output_type=_type)
            # if export_type == 'download':
            csv_string = df.to_csv(index=False, encoding='utf-8')
            csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
            return csv_string
        else:
            return None
    else:
        return None


@app.callback(
    Output('app2_error', 'children'),
    [
        Input('app2_button_submit', 'n_clicks'),
    ],
    [
        State('app2_sample_table', 'data'),
        State('app2_iso_table', 'data'),
    ])
def error(n_submit, sample_tb_rows, iso_tb_rows):
    if n_submit is not None:
        # Modify input for testing
        sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
        iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
        sample_tb_df = pd.DataFrame(sample_tb_dict)
        iso_tb_df = pd.DataFrame(iso_tb_dict)

        # Test input format
        test_passed_list, output_div_list = validate_sample_input(sample_df=sample_tb_df,
                                                                  iso_df=iso_tb_df,
                                                                  sample_schema=sample_dict_schema,
                                                                  iso_schema=iso_dict_schema)

        # Calculation starts
        if all(test_passed_list):
            return None
        else:
            return output_div_list
    else:
        return None


@app.callback(
    Output('app2_result', 'children'),
    [
        Input('app2_button_submit', 'n_clicks'),
    ],
    [
        State('y_type', 'value'),
        State('app2_sample_table', 'data'),
        State('app2_iso_table', 'data'),
        State('app2_iso_check', 'values'),
    ])
def output(n_submit, y_type, sample_tb_rows, iso_tb_rows, iso_changed):
    if n_submit is not None:
        # Modify input for testing
        sample_tb_dict = force_dict_to_numeric(input_dict_list=sample_tb_rows)
        iso_tb_dict = force_dict_to_numeric(input_dict_list=iso_tb_rows)
        sample_tb_df = pd.DataFrame(sample_tb_dict)
        iso_tb_df = pd.DataFrame(iso_tb_dict)

        # Test input format
        test_passed_list, output_div_list = validate_sample_input(sample_df=sample_tb_df,
                                                                  iso_df=iso_tb_df,
                                                                  sample_schema=compos_dict_schema,
                                                                  iso_schema=iso_dict_schema)

        # Calculation starts
        if all(test_passed_list):
            total_trans, div_list, o_stack = calculate_transmission_cg1d_and_form_stack_table(sample_tb_df=sample_tb_df,
                                                                                              iso_tb_df=iso_tb_df,
                                                                                              iso_changed=iso_changed)
            if y_type == 'transmission':
                output_div_list = [
                    html.H5('Sample transmission:'),
                    html.P('The total neutron transmission at CG-1D (ORNL): {} %'.format(round(total_trans, 3))),
                    html.Div([html.H5('Sample stack:'), html.Div(div_list)]),
                ]
            else:
                output_div_list = [
                    html.H5('Sample attenuation:'),
                    html.P('The total neutron attenuation at CG-1D (ORNL): {} %'.format(round(100 - total_trans, 3))),
                    html.Div([html.H5('Sample stack:'), html.Div(div_list)]),
                ]
            return output_div_list
        else:
            return None
    else:
        return None
