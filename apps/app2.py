import numpy as np
from ImagingReso._utilities import ev_to_angstroms
from ImagingReso._utilities import ev_to_s
from dash.dependencies import Input, Output, State
from _app import app
import urllib.parse
from _utilities import *

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

plot_data_filename = "plot_data.csv"

# Create app2 layout
layout = html.Div(
    [
        dcc.Link('Home', href='/'),
        html.Br(),
        dcc.Link('Cold neutron transmission', href='/apps/cg1d'),
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
                html.Div([
                    dt.DataTable(
                        rows=df_range.to_dict('records'),
                        # optional - sets the order of columns
                        columns=range_tb_header,
                        editable=False,
                        row_selectable=False,
                        filterable=False,
                        sortable=True,
                        id='range_table'
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
                                            id='e_step',
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
                                        dcc.Input(id='distance', type='number', value=16.45, min=1,
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
                            ], className=col_6,
                        ),
                    ], className='row',
                ),
            ]
        ),

        # Sample input
        html.H3('Sample info'),
        html.Div([
            html.Div(
                [
                    html.Button('+', id='button_add', n_clicks=0),
                    html.Button('-', id='button_del', n_clicks=0),
                    # html.Button('+', id='button_add', n_clicks_timestamp=0),
                    # html.Button('-', id='button_del', n_clicks_timestamp=0),
                ], className='row'
            ),

            dt.DataTable(
                rows=df_sample.to_dict('records'),
                # optional - sets the order of columns
                columns=sample_tb_header,
                editable=True,
                row_selectable=False,
                filterable=False,
                sortable=False,
                id='sample_table'
            ),
            dcc.Markdown(
                '''NOTE: density input can be omitted (leave as blank) only if the input formula is single element,
                 density available [here](http://periodictable.com/Properties/A/Density.al.html) will be used.'''),
            dcc.Checklist(id='iso_modified',
                          options=[
                              {'label': 'Modify isotopic ratios', 'value': True},
                          ], values=[],
                          ),
            html.Div(
                [
                    dcc.Markdown("""NOTE: Please edit **ONLY** the 'Isotopic ratio' column.
                        Editing of 'Sample info' will **RESET** contents in isotope table."""),
                    dt.DataTable(rows=iso_tb_df_default.to_dict('records'),
                                 columns=iso_table_header,
                                 editable=True,
                                 # editable={layer_name: False,
                                 #           ele_name: False,
                                 #           iso_name: True,
                                 #           },
                                 # row_selectable=True,
                                 filterable=True,
                                 sortable=True,
                                 id='iso_table'),
                ],
                id='iso_input',
                style={'visibility': 'hidden'},
                # style={'display': 'none'},
            ),
            html.Button('Submit', id='button_submit'),
        ]
        ),
        # Hidden Div to handle button action
        html.Div([
            html.Div(id='clicked_button', children='del:0 add:0 tog:0 last:nan', style={'display': 'none'})
        ]),
        html.Div(id='display_clicked', children=""),
        # Plot
        html.Div(
            [
                html.Div(id='plot_options', children=plot_option_div),
                html.Div(
                    [
                        dcc.Checklist(id='export_clip',
                                      options=[
                                          {'label': 'Clipboard', 'value': False},
                                      ], values=[],
                                      ),
                        html.A(
                            'Download Plot Data',
                            id='download_link',
                            download=plot_data_filename,
                            href="",
                            target="_blank",
                            style={'display': 'inline-block'},
                        ),
                    ], className='row'
                ),
                html.Div(id='plot'),
            ],
            id='plot_div',
            style={'display': 'none'}
        ),

        # Stack display
        html.Div(
            [
                # Transmission at CG-1D
                html.Div(id='result'),
                # Sample stack
                html.Div(id='stack'),
            ],
        ),
    ]
)


@app.callback(
    Output('range_table', 'rows'),
    [
        Input('e_range_slider', 'value'),
        Input('distance', 'value'),
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
        energy_name: [e_min, e_max],
        wave_name: [lambda_1, lambda_2],
        speed_name: [v_1, v_2],
        tof_name: [tof_1, tof_2],
        class_name: [class_1, class_2],
    })
    return _df_range.to_dict('records')


@app.callback(
    Output('clicked_button', 'children'),
    [
        Input('button_add', 'n_clicks'),
        Input('button_del', 'n_clicks')
    ],
    [
        State('clicked_button', 'children')
    ])
def updated_clicked(add_clicks, del_clicks, prev_clicks):
    prev_clicks = dict([i.split(':') for i in prev_clicks.split(' ')])
    last_clicked = 'nan'
    if del_clicks > int(prev_clicks['del']):
        last_clicked = 'del'
    elif add_clicks > int(prev_clicks['add']):
        last_clicked = 'add'
    cur_clicks = 'del:{} add:{} last:{}'.format(del_clicks, add_clicks, last_clicked)
    return cur_clicks


@app.callback(
    Output('sample_table', 'rows'),
    [
        Input('clicked_button', 'children'),
    ],
    [
        State('sample_table', 'rows'),
    ])
def add_del_row(clicked, sample_tb_rows):
    last_clicked = clicked[-3:]
    _df_sample = add_del_tb_rows(add_or_del=last_clicked, sample_tb_rows=sample_tb_rows)
    return _df_sample.to_dict('records')


@app.callback(
    Output('iso_table', 'rows'),
    [
        Input('sample_table', 'rows'),
    ])
def update_iso_table(sample_tb_rows):
    _df = form_iso_table(sample_tb_rows)
    return _df.to_dict('records')


@app.callback(
    Output('iso_input', 'style'),
    [
        Input('iso_modified', 'values'),
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
    Output('plot_div', 'style'),
    [
        Input('button_submit', 'n_clicks'),
    ])
def show_plot_options(n_submit):
    if n_submit is not None:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


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
        State('iso_table', 'rows'),
        State('iso_modified', 'values'),
    ])
def plot(n_submit, y_type, x_type, plot_scale, show_opt,
         range_tb_rows, e_step, distance_m,
         sample_tb_rows, iso_tb_rows,
         iso_changed):
    if n_submit is not None:
        o_reso = init_reso_from_tb(range_tb_rows, e_step)

        df_sample_tb = pd.DataFrame(sample_tb_rows)
        df_iso_tb = pd.DataFrame(iso_tb_rows)
        o_reso = unpack_sample_tb_df_and_add_layer(o_reso=o_reso, sample_tb_df=df_sample_tb)
        o_reso = unpack_iso_tb_df_and_update(o_reso=o_reso, iso_tb_df=df_iso_tb, iso_changed=iso_changed)

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
                dcc.Graph(id='reso_plot', figure=plotly_fig, className='container'),
            ]
        )


@app.callback(
    Output('download_link', 'href'),
    [
        Input('button_submit', 'n_clicks'),
        Input('y_type', 'value'),
        Input('x_type', 'value'),
        Input('show_opt', 'values'),
        Input('export_clip', 'values'),
    ],
    [
        State('range_table', 'rows'),
        State('e_step', 'value'),
        State('distance', 'value'),
        State('sample_table', 'rows'),
        State('iso_table', 'rows'),
        State('iso_modified', 'values'),
    ])
def export_plot_data(n_submit,
                     y_type, x_type, show_opt, export_clip,
                     range_tb_rows, e_step, distance_m,
                     sample_tb_rows, iso_tb_rows,
                     iso_changed):
    o_reso = init_reso_from_tb(range_tb_rows, e_step)

    df_sample_tb = pd.DataFrame(sample_tb_rows)
    df_iso_tb = pd.DataFrame(iso_tb_rows)
    o_reso = unpack_sample_tb_df_and_add_layer(o_reso=o_reso, sample_tb_df=df_sample_tb)
    o_reso = unpack_iso_tb_df_and_update(o_reso=o_reso, iso_tb_df=df_iso_tb, iso_changed=iso_changed)

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


@app.callback(
    Output('result', 'children'),
    [
        Input('button_submit', 'n_clicks'),
    ],
    [
        State('y_type', 'value'),
        State('sample_table', 'rows'),
        State('iso_table', 'rows'),
        State('iso_modified', 'values'),
    ])
def output(n_clicks, y_type, sample_tb_rows, iso_tb_rows, iso_changed):
    if n_clicks is not None:
        total_trans, div_list = calculate_transmission_cg1d_and_form_stack_table(sample_tb_rows,
                                                                                 iso_tb_rows,
                                                                                 iso_changed)
        if y_type == 'transmission':
            return html.Div(
                [
                    html.H5('Sample transmission:'),
                    html.P('The total neutron transmission at CG-1D (ORNL): {} %'.format(round(total_trans, 3))),
                    html.Div([html.H5('Sample stack:'), html.Div(div_list)])
                ])
        else:
            return html.Div(
                [
                    html.H5('Sample attenuation:'),
                    html.P('The total neutron attenuation at CG-1D (ORNL): {} %'.format(round(100 - total_trans, 3))),
                    html.Div([html.H5('Sample stack:'), html.Div(div_list)])
                ])
