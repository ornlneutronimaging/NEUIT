from dash.dependencies import Input, Output, State

from _app import app
from _utilities import *
import plotly.tools as tls
import matplotlib.pyplot as plt
from bem import xscalc

# Bragg-edge tool

app_name = 'app5'
app_id_dict = init_app_ids(app_name=app_name)

# Create app layout
layout = html.Div(
    [
        init_app_links(current_app=app_name, app_dict_all=app_dict),

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

        # Hidden div to store json
        html.Div(id=app_id_dict['hidden_df_json_id'], style={'display': 'none'}),

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
                                                  {'label': 'Elastic', 'value': 'el'},
                                                  {'label': 'Inelastic', 'value': 'inel'},
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
                html.Div(id=app_id_dict['hidden_df_tb_div']),

                # Transmission at CG-1D and stack info
                html.Div(id=app_id_dict['result_id']),
            ],
            id=app_id_dict['output_id'],
            style={'display': 'none'},
        ),
    ]
)


@app.callback(
    [
        Output(app_id_dict['plot_div_id'], 'children'),
        Output(app_id_dict['output_id'], 'style'),
        Output(app_id_dict['cif_upload_fb_id'], 'children'),
        Output(app_id_dict['hidden_df_json_id'], 'children'),
    ],
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
        Input(app_id_dict['cif_upload_id'], 'contents'),
        Input('x_type', 'value'),
        Input('y_type', 'value'),
        Input('plot_scale', 'value'),
        Input('xs_type', 'value'),
    ],
    [
        State(app_id_dict['cif_upload_id'], 'filename'),
        State(app_id_dict['cif_upload_id'], 'last_modified'),
        State(app_id_dict['temperature_id'], 'value'),
        State(app_id_dict['band_min_id'], 'value'),
        State(app_id_dict['band_max_id'], 'value'),
        State(app_id_dict['band_step_id'], 'value'),
        State(app_id_dict['output_id'], 'style'),
    ])
def plot(n_submit, cif_uploads, x_type, y_type, plot_scale, xs_type,
         cif_names, cif_last_modified_time,
         temperature_K, band_min, band_max, band_step,
         output_style):
    error_div_list = []
    data_fb = []
    xs_dict = {}
    wavelengths_A = np.arange(band_min, band_max, band_step)
    if cif_uploads is not None:
        for each_index, each_content in enumerate(cif_uploads):
            _cif_struc, data_error_div = parse_cif_upload(content=each_content,
                                                          fname=cif_names[each_index],
                                                          )
            if data_error_div is None:
                _name_only = cif_names[each_index].split('.')[0]
                print("'{}' loaded. Calculating...".format(cif_names[each_index]))
                xscalculator = xscalc.XSCalculator(_cif_struc, temperature_K, max_diffraction_index=4)
                if 'total' in xs_type:
                    xs_dict[_name_only + '_total'] = xscalculator.xs(wavelengths_A)
                if 'el' in xs_type:
                    xs_dict[_name_only + '_coh_el'] = xscalculator.xs_coh_el(wavelengths_A)
                    xs_dict[_name_only + '_inc_el'] = xscalculator.xs_inc_el(wavelengths_A)
                if 'inel' in xs_type:
                    xs_dict[_name_only + '_coh_inel'] = xscalculator.xs_coh_inel(wavelengths_A)
                    xs_dict[_name_only + '_inc_inel'] = xscalculator.xs_inc_inel(wavelengths_A)
                data_fb.append(html.Div(['\u2705 Data file "{}" uploaded.'.format(cif_names[each_index])]))
            else:
                data_fb.append(data_error_div)
                error_div_list.append(data_error_div)


    # Plot
    if len(error_div_list) == 0:
        df_plot = pd.DataFrame.from_dict(xs_dict)
        if y_type == 'attenuation':
            df_plot = 1 - df_plot
        if x_type == 'energy':
            x_type_name = energy_name
            df_plot[x_type_name] = ir_util.angstroms_to_ev(wavelengths_A)
        else:
            x_type_name = wave_name
            df_plot[x_type_name] = wavelengths_A
        df_plot = df_plot.set_index(x_type_name)
        x_label = x_type_to_x_label(x_type)
        y_label = y_type_to_y_label(y_type)
        jsonized_df = df_plot.to_json(orient='split', date_format='iso')

        # Plot
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        try:
            ax1 = df_plot.plot(legend=False, ax=ax1)
            output_style['display'] = 'block'
        except TypeError:
            pass
        ax1.set_ylabel(y_label)
        ax1.set_xlabel(x_label)
        plotly_fig = tls.mpl_to_plotly(fig)

        # Layout
        plotly_fig.layout.showlegend = True
        plotly_fig.layout.autosize = True
        plotly_fig.layout.height = 600
        plotly_fig.layout.width = 900
        plotly_fig.layout.margin = {'b': 52, 'l': 80, 'pad': 0, 'r': 15, 't': 15}
        plotly_fig.layout.xaxis1.tickfont.size = 15
        plotly_fig.layout.xaxis1.titlefont.size = 18
        plotly_fig.layout.yaxis1.tickfont.size = 15
        plotly_fig.layout.yaxis1.titlefont.size = 18
        plotly_fig.layout.xaxis.autorange = True
        plotly_fig['layout']['yaxis']['autorange'] = True

        if plot_scale == 'logx':
            plotly_fig['layout']['xaxis']['type'] = 'log'
            plotly_fig['layout']['yaxis']['type'] = 'linear'
        elif plot_scale == 'logy':
            if y_type not in ['attenuation', 'transmission']:
                plotly_fig['layout']['xaxis']['type'] = 'linear'
                plotly_fig['layout']['yaxis']['type'] = 'log'
        elif plot_scale == 'loglog':
            if y_type not in ['attenuation', 'transmission']:
                plotly_fig['layout']['xaxis']['type'] = 'log'
                plotly_fig['layout']['yaxis']['type'] = 'log'
        else:
            plotly_fig['layout']['xaxis']['type'] = 'linear'
            plotly_fig['layout']['yaxis']['type'] = 'linear'
        return html.Div([dcc.Graph(figure=plotly_fig,
                                   id=app_id_dict['plot_fig_id'])]), output_style, data_fb, None
    else:
        output_style['display'] = 'none'
        return plot_loading, output_style, data_fb, None
