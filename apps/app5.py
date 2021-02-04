from dash.dependencies import Input, Output, State

from _app import app
from _utilities import *
import matplotlib.pyplot as plt
from bem import xscalc

# Bragg-edge tool

app_name = 'app5'
app_id_dict = init_app_ids(app_name=app_name)

# Create app layout
layout = html.Div(
    [
        init_app_links(current_app=app_name, app_dict_all=app_dict),
        init_app_about(current_app=app_name, app_id_dict=app_id_dict),
        # Experiment input
        html.Div(
            [
                html.H3('Global parameters:'),
                html.Div(
                    [

                        html.Div(
                            [
                                html.H6('Temperature (K):'),
                                dcc.Input(id=app_id_dict['temperature_id'],
                                          type='number',
                                          value=temperature_default,
                                          min=0,
                                          inputMode='numeric',
                                          step=0.1,
                                          ),
                            ], className=col_width_3,
                        ),

                        # html.Div(
                        #     [
                        #         html.H6('Source-to-detector (m):'),
                        #         dcc.Input(id=app_id_dict['distance_id'],
                        #                   type='number',
                        #                   value=distance_default,
                        #                   min=0,
                        #                   inputMode='numeric',
                        #                   step=0.01,
                        #                   ),
                        #     ], className=col_width_3,
                        # ),

                    ], className='row', style={'verticalAlign': 'middle'},
                ),
            ], className='row', style={'verticalAlign': 'middle'},
        ),

        html.Div(
            [
                html.H6('Wavelength band:'),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P('Min. (\u212B) :'),
                                dcc.Input(id=app_id_dict['band_min_id'], type='number',
                                          inputMode='numeric',
                                          placeholder='Min.',
                                          step=0.001,
                                          value=0.05,
                                          ),
                            ], className=col_width_3,
                        ),
                        html.Div(
                            [
                                html.P('Max. (\u212B):'),
                                dcc.Input(id=app_id_dict['band_max_id'], type='number',
                                          inputMode='numeric',
                                          placeholder='Max.',
                                          step=0.001,
                                          value=5.5,
                                          ),
                            ], className=col_width_3,
                        ),
                        html.Div(
                            [
                                html.P('Step (\u212B):'),
                                dcc.Input(id=app_id_dict['band_step_id'], type='number',
                                          inputMode='numeric',
                                          placeholder='Max.',
                                          step=0.001,
                                          value=0.005,
                                          ),
                            ], className=col_width_3,
                        ),
                    ], className='row', style={'verticalAlign': 'middle'},
                ),
            ],
            className='row',
            style={'verticalAlign': 'middle'},
        ),

        html.H3('Upload cif file/files:'),

        html.Div(
            [
                dcc.Upload(id=app_id_dict['cif_upload_id'],
                           children=html.Div([
                               'Drag and Drop or ',
                               html.A('Select Files'),
                           ]),
                           style={
                               'width': '100%',
                               'height': '60px',
                               'lineHeight': '60px',
                               'borderWidth': '1px',
                               'borderStyle': 'dashed',
                               'borderRadius': '5px',
                               'textAlign': 'center',
                               'margin': '10px'
                           },
                           # Allow multiple files to be uploaded
                           multiple=True,
                           last_modified=0,
                           ),
                html.Div(id=app_id_dict['cif_upload_fb_id']),
                html.Button('Submit', id=app_id_dict['submit_button_id'], n_clicks_timestamp=0),
                html.Div(id=app_id_dict['hidden_upload_time_id'], style={'display': 'none'}, children=0),
            ]
        ),

        # Error message div
        html.Div(id=app_id_dict['error_id'], children=None),

        # Hidden div to store df_all json
        html.Div(id=app_id_dict['hidden_df_json_id'], style={'display': 'none'}),

        # Hidden div to store df_export json
        html.Div(id=app_id_dict['hidden_df_export_json_id'], style={'display': 'none'}),

        # Output div
        html.Div(
            [
                # Plot options
                html.H3('Plot:'),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P('X options: '),
                                dcc.RadioItems(id='x_type',
                                               options=[
                                                   {'label': 'Wavelength (\u212B)', 'value': 'lambda'},
                                                   {'label': 'Energy (eV)', 'value': 'energy'},
                                               ],
                                               value='lambda',
                                               )
                            ], className=col_width_3
                        ),
                        html.Div(
                            [
                                html.P('Y options: '),
                                dcc.RadioItems(id='y_type',
                                               options=[
                                                   # {'label': 'Transmission', 'value': 'transmission'},
                                                   # {'label': 'Attenuation', 'value': 'attenuation'},
                                                   # {'label': 'Attenuation coefficient', 'value': 'mu_per_cm'},
                                                   # {'label': "Cross-section (weighted)", 'value': 'sigma'},
                                                   {'label': 'Cross-section (raw)', 'value': 'sigma_raw'},
                                               ],
                                               value='sigma_raw',
                                               )
                            ], className=col_width_3
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
                                               # n_clicks_timestamp=0,
                                               )
                            ], className=col_width_3
                        ),
                        html.Div(
                            [
                                html.P('Interactions: '),
                                dcc.Checklist(id='xs_type',
                                              options=[
                                                  {'label': 'Total', 'value': 'total'},
                                                  {'label': 'Absorption', 'value': 'abs'},
                                                  {'label': 'Elastic scattering', 'value': 'el'},
                                                  {'label': 'Inelastic scattering', 'value': 'inel'},
                                                  # {'label': 'Coherent', 'value': 'coh'},
                                                  # {'label': 'Incoherent', 'value': 'inc'},
                                              ],
                                              value=['total'],
                                              # n_clicks_timestamp=0,
                                              )
                            ], className=col_width_3
                        ),
                    ], className='row'
                ),

                # Plot
                html.Div(id=app_id_dict['plot_div_id'], children=plot_loading, className='container'),

                # Export plot data button
                html.Div(
                    [
                        dcc.Checklist(
                            id=app_id_dict['display_plot_data_id'],
                            options=[
                                {'label': 'Display plotted data', 'value': 'display'},
                            ],
                            value=[],
                            labelStyle={'display': 'inline-block'}
                        ),
                    ], className='row'
                ),

                # Data table for the plotted data
                html.Div(id=app_id_dict['df_export_tb_div']),

                # Transmission at CG-1D and stack info
                html.Div(id=app_id_dict['result_id']),
            ],
            id=app_id_dict['output_id'],
            style={'display': 'none'},
        ),
    ]
)


@app.callback(
    Output(app_id_dict['app_info_id'], 'style'),
    [
        Input(app_id_dict['more_about_app_id'], 'value'),
    ],
    [
        State(app_id_dict['app_info_id'], 'style'),
    ])
def show_hide_band_input(more_info, style):
    if more_info != ['more']:
        style['display'] = 'none'
    else:
        style['display'] = 'block'
    return style


@app.callback(
    [
        Output(app_id_dict['cif_upload_fb_id'], 'children'),
        Output(app_id_dict['error_id'], 'children'),
    ],
    [
        Input(app_id_dict['cif_upload_id'], 'filename'),
    ])
def upload_feedback(cif_names):
    data_fb_list = []
    error_div_list = []
    if cif_names is not None:
        for each_fname in cif_names:
            if '.cif' in each_fname:
                data_fb_list.append(html.Div(['\u2705 Data file "{}" uploaded.'.format(each_fname)]))
            else:
                error_div = html.Div(
                    ["\u274C Type error: '{}' is not supported, only '.cif' is ""supported.".format(each_fname)])
                error_div_list.append(error_div)
        if len(error_div_list) == 0:
            test_passed = True
        else:
            test_passed = error_div_list
        return data_fb_list, test_passed
    else:
        return [None], [None]


@app.callback(
    Output(app_id_dict['output_id'], 'style'),
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
        Input(app_id_dict['error_id'], 'children'),
    ])
def show_output_div(n_submit, test_passed):
    if n_submit is not None:
        if test_passed is True:
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@app.callback(
    [
        Output(app_id_dict['hidden_df_json_id'], 'children'),
    ],
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
    ],
    [
        State(app_id_dict['error_id'], 'children'),
        State(app_id_dict['cif_upload_id'], 'contents'),
        State(app_id_dict['cif_upload_id'], 'filename'),
        State(app_id_dict['temperature_id'], 'value'),
        State(app_id_dict['band_min_id'], 'value'),
        State(app_id_dict['band_max_id'], 'value'),
        State(app_id_dict['band_step_id'], 'value'),
    ])
def store_bragg_df_in_json(n_submit, test_passed,
                           cif_uploads, cif_names,
                           temperature_K, band_min, band_max, band_step,
                           ):
    if test_passed:
        xs_dict = {}
        wavelengths_A = np.arange(band_min, band_max, band_step)
        if cif_uploads is not None:
            for each_index, each_content in enumerate(cif_uploads):
                _cif_struc = parse_cif_upload(content=each_content)
                _name_only = cif_names[each_index].split('.')[0]
                print("'{}', calculating cross-sections...".format(cif_names[each_index]))
                xscalculator = xscalc.XSCalculator(_cif_struc, temperature_K, max_diffraction_index=4)
                xs_dict[_name_only + ' (total)'] = xscalculator.xs(wavelengths_A)
                xs_dict[_name_only + ' (abs)'] = xscalculator.xs_abs(wavelengths_A)
                xs_dict[_name_only + ' (coh el)'] = xscalculator.xs_coh_el(wavelengths_A)
                xs_dict[_name_only + ' (inc el)'] = xscalculator.xs_inc_el(wavelengths_A)
                xs_dict[_name_only + ' (coh inel)'] = xscalculator.xs_coh_inel(wavelengths_A)
                xs_dict[_name_only + ' (inc inel)'] = xscalculator.xs_inc_inel(wavelengths_A)
                print("Calculation done.")
            df_y = pd.DataFrame.from_dict(xs_dict)
            df_x = pd.DataFrame()
            df_x[wave_name] = wavelengths_A
            df_x[energy_name] = ir_util.angstroms_to_ev(wavelengths_A)
            datasets = {
                'x': df_x.to_json(orient='split', date_format='iso'),
                'y': df_y.to_json(orient='split', date_format='iso'),
            }
            return [json.dumps(datasets)]
        else:
            return [None]


@app.callback(
    [
        Output(app_id_dict['plot_div_id'], 'children'),
        Output(app_id_dict['hidden_df_export_json_id'], 'children'),
    ],
    [
        Input(app_id_dict['hidden_df_json_id'], 'children'),
        Input(app_id_dict['error_id'], 'children'),
        Input('x_type', 'value'),
        Input('y_type', 'value'),
        Input('plot_scale', 'value'),
        Input('xs_type', 'value'),
    ],
    [
        State(app_id_dict['cif_upload_id'], 'filename'),
    ])
def plot(jsonified_data, test_passed, x_type, y_type, plot_scale, xs_type, fnames):
    if test_passed and jsonified_data is not None:
        df_dict = load_dfs(jsonified_data=jsonified_data)
        df_x = df_dict['x']
        df_y = df_dict['y']

        # Form selected Y df
        to_plot_list = []
        for each_fname in fnames:
            _name_only = each_fname.split('.')[0]
            if 'total' in xs_type:
                to_plot_list.append(_name_only + ' (total)')
            if 'abs' in xs_type:
                to_plot_list.append(_name_only + ' (abs)')
            if 'el' in xs_type:
                to_plot_list.append(_name_only + ' (coh el)')
                to_plot_list.append(_name_only + ' (inc el)')
            if 'inel' in xs_type:
                to_plot_list.append(_name_only + ' (coh inel)')
                to_plot_list.append(_name_only + ' (inc inel)')
        df_to_plot = df_y[to_plot_list]
        if y_type == 'attenuation':
            df_to_plot = 1 - df_y

        # Add X column
        x_tag = x_type_to_x_tag(x_type)
        df_to_plot.insert(loc=0, column=x_tag, value=df_x[x_tag])
        y_label = y_type_to_y_label(y_type)

        jsonized_plot_df = df_to_plot.to_json(orient='split', date_format='iso')

        # Plot in matplotlib
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        try:
            ax1 = df_to_plot.set_index(keys=x_tag).plot(legend=False, ax=ax1)
        except TypeError:
            pass
        ax1.set_ylabel(y_label)

        # Convert to plotly and format layout
        plotly_fig = shape_matplot_to_plotly(fig=fig, y_type=y_type, plot_scale=plot_scale)

        return html.Div([dcc.Graph(figure=plotly_fig,
                                   id=app_id_dict['plot_fig_id'])]), [json.dumps(jsonized_plot_df)]
    else:
        return plot_loading, [None]


@app.callback(
    [
        Output(app_id_dict['df_export_tb_div'], 'children'),
    ],
    [
        Input(app_id_dict['display_plot_data_id'], 'value'),
        Input(app_id_dict['hidden_df_export_json_id'], 'children'),
    ],
    [
        State(app_id_dict['error_id'], 'children'),
    ])
def display_plot_data_tb(display_check, jsonized_df_export, test_passed):
    if display_check == ['display']:
        if test_passed is True:
            dataset = json.loads(jsonized_df_export[0])
            df_to_export = pd.read_json(dataset, orient='split')
            df_tb_div_list = [
                html.Hr(),
                dt.DataTable(
                    id=app_id_dict['df_export_tb'],
                    data=df_to_export.to_dict('records'),
                    columns=[{'name': each_col, 'id': each_col} for each_col in df_to_export.columns],
                    export_format='csv',
                    style_data_conditional=[striped_rows],
                    fixed_rows={'headers': True, 'data': 0},
                    style_table={
                        'maxHeight': '300',
                        'overflowY': 'scroll',
                    },
                )
            ]
            return [df_tb_div_list]
        else:
            return [None]
    else:
        return [None]
