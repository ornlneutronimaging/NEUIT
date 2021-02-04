from dash.dependencies import Input, Output, State

from _app import app
from _utilities import *
import plotly.tools as tls
import matplotlib.pyplot as plt

# Time-of-flight plotter

app_name = 'app4'
app_id_dict = init_app_ids(app_name=app_name)

# Create app layout

layout = html.Div(
    [
        init_app_links(current_app=app_name, app_dict_all=app_dict),
        init_app_about(current_app=app_name, app_id_dict=app_id_dict),
        # Experiment input
        html.Div(
            [
                html.H3('Instrument Parameters:'),
                html.Div(
                    [
                        # html.Div(
                        #     [
                        #         html.H6('Temperature (K):'),
                        #         dcc.Input(id=app_id_dict['temperature_id'],
                        #                   type='number',
                        #                   value=temperature_default,
                        #                   min=0,
                        #                   inputMode='numeric',
                        #                   step=0.1,
                        #                   ),
                        #     ], className=col_width_3,
                        # ),

                        html.Div(
                            [
                                html.H6('Source-to-detector (m):'),
                                dcc.Input(id=app_id_dict['distance_id'],
                                          type='number',
                                          value=distance_default,
                                          min=0,
                                          inputMode='numeric',
                                          step=0.01,
                                          ),
                            ], className=col_width_3,
                        ),

                        html.Div(
                            [
                                html.H6('Delay (\u03BCs):'),
                                dcc.Input(id=app_id_dict['delay_id'],
                                          type='number',
                                          value=delay_default,
                                          min=0,
                                          inputMode='numeric',
                                          step=0.01,
                                          ),
                            ], className=col_width_3,
                        ),
                    ], className='row', style={'verticalAlign': 'middle'},
                ),
            ], className='row', style={'verticalAlign': 'middle'},
        ),

        html.H3('Upload files:'),

        html.Div(
            [
                html.H6('Spectrum:'),
                dcc.Upload(id=app_id_dict['spectra_upload_id'],
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
                           multiple=False,
                           last_modified=0,
                           ),
                html.Div(id=app_id_dict['spectra_upload_fb_id']),

                html.H6('Data:'),
                dcc.Upload(id=app_id_dict['data_upload_id'],
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
                html.Div(id=app_id_dict['data_upload_fb_id']),

                html.H6('Background (optional):'),
                dcc.Checklist(
                    id=app_id_dict['background_check_id'],
                    options=[
                        {'label': 'Ignore loaded background', 'value': 'ignore'},
                    ],
                    value=[],
                    labelStyle={'display': 'inline-block'}
                ),
                dcc.Upload(id=app_id_dict['background_upload_id'],
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
                           multiple=False,
                           last_modified=0,
                           ),
                html.Div(id=app_id_dict['background_upload_fb_id']),

                html.Div(id=app_id_dict['hidden_upload_time_id'], style={'display': 'none'}, children=0),
            ]
        ),

        # Error message div
        html.Div(id=app_id_dict['error_id'], children=None),

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
                                                   {'label': 'Energy (eV)', 'value': 'energy'},
                                                   {'label': 'Wavelength (\u212B)', 'value': 'lambda'},
                                                   {'label': 'Time-of-flight (\u03BCs)', 'value': 'time'},
                                                   {'label': 'Image index (#)', 'value': 'number'},
                                               ],
                                               value='number',
                                               # n_clicks_timestamp=0,
                                               )
                            ], className=col_width_3
                        ),
                        html.Div(
                            [
                                html.P('Y options: '),
                                dcc.RadioItems(id='y_type',
                                               options=[
                                                   {'label': 'Transmission', 'value': 'transmission'},
                                                   {'label': 'Attenuation', 'value': 'attenuation'},
                                               ],
                                               value='transmission',
                                               # n_clicks_timestamp=0,
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
                    ], className='row'
                ),

                # Plot
                html.Div(id=app_id_dict['plot_div_id'], children=plot_loading, className='container'),

                # # Transmission at CG-1D and stack info
                # html.Div(id=app_id_dict['result_id']),
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
        Output(app_id_dict['plot_div_id'], 'children'),
        Output(app_id_dict['output_id'], 'style'),
        Output(app_id_dict['spectra_upload_fb_id'], 'children'),
        Output(app_id_dict['data_upload_fb_id'], 'children'),
        Output(app_id_dict['background_upload_fb_id'], 'children'),
    ],
    [
        Input(app_id_dict['spectra_upload_id'], 'contents'),
        Input(app_id_dict['data_upload_id'], 'contents'),
        Input(app_id_dict['background_upload_id'], 'contents'),
        Input(app_id_dict['background_check_id'], 'value'),
        Input(app_id_dict['distance_id'], 'value'),
        Input(app_id_dict['delay_id'], 'value'),
        Input('x_type', 'value'),
        Input('y_type', 'value'),
        Input('plot_scale', 'value'),
    ],
    [
        State(app_id_dict['spectra_upload_id'], 'filename'),
        State(app_id_dict['spectra_upload_id'], 'last_modified'),
        State(app_id_dict['data_upload_id'], 'filename'),
        State(app_id_dict['data_upload_id'], 'last_modified'),
        State(app_id_dict['background_upload_id'], 'filename'),
        State(app_id_dict['background_upload_id'], 'last_modified'),
        State(app_id_dict['output_id'], 'style'),
    ])
def plot(spectra_contents, data_contents, bcgd_contents, bcgd_ignore, distance, delay, x_type, y_type, plot_scale,
         spectra_names, spectra_last_modified_time, data_names, data_last_modified_time,
         bcgd_names, bcgd_last_modified_time,
         output_style):
    error_div_list = []
    df_plot = pd.DataFrame()
    loaded = []
    spectra_fb = []
    data_fb = []
    bcgd_fb = []
    if spectra_contents is not None:
        df_spectra, spectra_error_div = parse_content(content=spectra_contents,
                                                      name=spectra_names,
                                                      header=None)
        if spectra_error_div is None:
            spectra_fb.append(html.Div(['\u2705 Spectra file "{}" uploaded.'.format(spectra_names)]))
            loaded.append('spectra')
        else:
            spectra_fb.append(spectra_error_div)
            error_div_list.append(spectra_error_div)

    if data_contents is not None:
        for each_index, each_content in enumerate(data_contents):
            _df_data, data_error_div = parse_content(content=each_content,
                                                     name=data_names[each_index],
                                                     header=0)
            if data_error_div is None:
                df_plot[data_names[each_index]] = _df_data['Y']
                loaded.append('data')
                data_fb.append(html.Div(['\u2705 Data file "{}" uploaded.'.format(data_names[each_index])]))
            else:
                data_fb.append(data_error_div)
                error_div_list.append(data_error_div)
    if bcgd_contents is not None:
        df_bcgd, bcgd_error_div = parse_content(content=bcgd_contents,
                                                name=bcgd_names,
                                                header=0)
        if bcgd_error_div is None:
            bcgd_fb.append(html.Div(['\u2705 Background file "{}" uploaded.'.format(bcgd_names)]))
            loaded.append('background')
        else:
            bcgd_fb.append(bcgd_error_div)

    # Verify the length of uploaded files
    if 'spectra' in loaded and 'data' in loaded:
        if len(df_plot) != len(df_spectra):
            data_len_error = html.Div(
                ["\u274C The length of data file ({}) is not the same as spectra file ({}).".format(
                    len(df_plot), len(df_spectra))])
            data_fb.append(data_len_error)
            error_div_list.append(data_len_error)
        if 'background' in loaded:
            if len(df_bcgd) != len(df_plot):
                bcgd_len_error = html.Div(
                    [
                        "\u274C Unable to remove background. The length of background file ({}) is not the same as data file ({}).".format(
                            len(df_bcgd), len(df_plot))])
                bcgd_fb.append(bcgd_len_error)
    # Plot
    if len(error_div_list) == 0:
        if 'spectra' in loaded and 'data' in loaded:
            if 'background' in loaded:
                if len(bcgd_fb) == 1:
                    if bcgd_ignore != ['ignore']:
                        df_plot = df_plot.div(df_bcgd.Y, axis=0)
            if y_type == 'attenuation':
                df_plot = 1 - df_plot
            df_plot['X'] = df_spectra[0]
            df_plot = shape_df_to_plot(x_type=x_type, df=df_plot, distance=distance, delay=delay)
            x_label = x_type_to_x_label(x_type)
            y_label = y_type_to_y_label(y_type)
            output_style['display'] = 'block'
            fig = plt.figure()
            ax1 = fig.add_subplot(111)
            # Plot
            try:
                ax1 = df_plot.set_index(keys='X').plot(legend=False, ax=ax1)
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
                                       id=app_id_dict['plot_fig_id'])]), output_style, spectra_fb, data_fb, bcgd_fb
        else:
            output_style['display'] = 'none'
            return plot_loading, output_style, spectra_fb, data_fb, bcgd_fb
    else:
        output_style['display'] = 'none'
        return None, output_style, spectra_fb, data_fb, bcgd_fb
