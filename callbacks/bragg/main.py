from dash.dependencies import Input, Output, State
from dash import dash_table as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import time

import ImagingReso._utilities as ir_util
from app import app
from callbacks.utilities.initialization import (init_app_ids, striped_rows, plot_loading, resubmit)
import callbacks.utilities.constants as constants
from callbacks.utilities.plot import shape_matplot_to_plotly
from callbacks.utilities.all_apps import (y_type_to_y_label, x_type_to_x_tag, load_dfs,
                                          create_table_output_file_name, format_data,
                                          clean_data_tab, update_xs_dict, update_list_to_plot,
                                          clean_texture_data, boolean_value_of_texture_checklist_to_flag,
                                          boolean_value_of_grain_size_checklist_to_flag)

from callbacks.utilities.bragg import parse_cif_file, parse_txt_file
from callbacks.utilities.resonance import fill_df_x_types
from callbacks.utilities.constants import *


app_name = 'bragg'
app_id_dict = init_app_ids(app_name=app_name)


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


# submit button clicked
@app.callback(
    [
        Output(app_id_dict['hidden_df_json_id'], 'children'),
        Output(app_id_dict['no_error_id'], 'children'),
        Output(app_id_dict['output_id'], 'style'),
        Output(app_id_dict['general_processing_errors'], 'children')
    ],
    [
        Input(app_id_dict['submit_button_id'], 'n_clicks'),
    ],
    [
        State(app_id_dict['data_table_tab1'], 'data'),
        State(app_id_dict['a_tab1'], 'value'),
        State(app_id_dict['b_tab1'], 'value'),
        State(app_id_dict['c_tab1'], 'value'),
        State(app_id_dict['alpha_tab1'], 'value'),
        State(app_id_dict['beta_tab1'], 'value'),
        State(app_id_dict['gamma_tab1'], 'value'),
        State(app_id_dict['no_error_tab1'], 'children'),
        State(app_id_dict['texture_checklist_tab1'], 'value'),
        State(app_id_dict['texture_table_tab1'], 'data'),
        State(app_id_dict['grain_size_checklist_tab1'], 'value'),
        State(app_id_dict['grain_size_input_tab1'], 'value'),

        State(app_id_dict['data_table_tab2'], 'data'),
        State(app_id_dict['a_tab2'], 'value'),
        State(app_id_dict['b_tab2'], 'value'),
        State(app_id_dict['c_tab2'], 'value'),
        State(app_id_dict['alpha_tab2'], 'value'),
        State(app_id_dict['beta_tab2'], 'value'),
        State(app_id_dict['gamma_tab2'], 'value'),
        State(app_id_dict['no_error_tab2'], 'children'),
        State(app_id_dict['texture_checklist_tab2'], 'value'),
        State(app_id_dict['texture_table_tab2'], 'data'),
        State(app_id_dict['grain_size_checklist_tab2'], 'value'),
        State(app_id_dict['grain_size_input_tab2'], 'value'),

        State(app_id_dict['data_table_tab3'], 'data'),
        State(app_id_dict['a_tab3'], 'value'),
        State(app_id_dict['b_tab3'], 'value'),
        State(app_id_dict['c_tab3'], 'value'),
        State(app_id_dict['alpha_tab3'], 'value'),
        State(app_id_dict['beta_tab3'], 'value'),
        State(app_id_dict['gamma_tab3'], 'value'),
        State(app_id_dict['no_error_tab3'], 'children'),
        State(app_id_dict['texture_checklist_tab3'], 'value'),
        State(app_id_dict['texture_table_tab3'], 'data'),
        State(app_id_dict['grain_size_checklist_tab3'], 'value'),
        State(app_id_dict['grain_size_input_tab3'], 'value'),

        State(app_id_dict['data_table_tab4'], 'data'),
        State(app_id_dict['a_tab4'], 'value'),
        State(app_id_dict['b_tab4'], 'value'),
        State(app_id_dict['c_tab4'], 'value'),
        State(app_id_dict['alpha_tab4'], 'value'),
        State(app_id_dict['beta_tab4'], 'value'),
        State(app_id_dict['gamma_tab4'], 'value'),
        State(app_id_dict['no_error_tab4'], 'children'),
        State(app_id_dict['texture_checklist_tab4'], 'value'),
        State(app_id_dict['texture_table_tab4'], 'data'),
        State(app_id_dict['grain_size_checklist_tab4'], 'value'),
        State(app_id_dict['grain_size_input_tab4'], 'value'),

        State(app_id_dict['data_table_tab5'], 'data'),
        State(app_id_dict['a_tab5'], 'value'),
        State(app_id_dict['b_tab5'], 'value'),
        State(app_id_dict['c_tab5'], 'value'),
        State(app_id_dict['alpha_tab5'], 'value'),
        State(app_id_dict['beta_tab5'], 'value'),
        State(app_id_dict['gamma_tab5'], 'value'),
        State(app_id_dict['no_error_tab5'], 'children'),
        State(app_id_dict['texture_checklist_tab5'], 'value'),
        State(app_id_dict['texture_table_tab5'], 'data'),
        State(app_id_dict['grain_size_checklist_tab5'], 'value'),
        State(app_id_dict['grain_size_input_tab5'], 'value'),

        State(app_id_dict['temperature_id'], 'value'),
        State(app_id_dict['distance_id'], 'value'),
        State(app_id_dict['delay_id'], 'value'),
        State(app_id_dict['band_min_id'], 'value'),
        State(app_id_dict['band_max_id'], 'value'),
        State(app_id_dict['band_step_id'], 'value'),
    ]
)
def show_output_div(n_submit,
                    data_tab1, a_tab1, b_tab1, c_tab1, alpha_tab1, beta_tab1, gamma_tab1, no_error_tab1,
                    texture_flag_tab1, texture_data_tab1,
                    grain_size_flag_tab1, grain_size_tab1,
                    data_tab2, a_tab2, b_tab2, c_tab2, alpha_tab2, beta_tab2, gamma_tab2, no_error_tab2,
                    texture_flag_tab2, texture_data_tab2,
                    grain_size_flag_tab2, grain_size_tab2,
                    data_tab3, a_tab3, b_tab3, c_tab3, alpha_tab3, beta_tab3, gamma_tab3, no_error_tab3,
                    texture_flag_tab3, texture_data_tab3,
                    grain_size_flag_tab3, grain_size_tab3,
                    data_tab4, a_tab4, b_tab4, c_tab4, alpha_tab4, beta_tab4, gamma_tab4, no_error_tab4,
                    texture_flag_tab4, texture_data_tab4,
                    grain_size_flag_tab4, grain_size_tab4,
                    data_tab5, a_tab5, b_tab5, c_tab5, alpha_tab5, beta_tab5, gamma_tab5, no_error_tab5,
                    texture_flag_tab5, texture_data_tab5,
                    grain_size_flag_tab5, grain_size_tab5,
                    temperature, distance, delay,
                    band_min, band_max, band_step):

    something_to_plot = False
    if n_submit is not None:

        wavelengths_A = np.arange(band_min, band_max, band_step)
        xs_dict = {}

        data_tab1 = clean_data_tab(data_tab1)
        data_tab2 = clean_data_tab(data_tab2)
        data_tab3 = clean_data_tab(data_tab3)
        data_tab4 = clean_data_tab(data_tab4)
        data_tab5 = clean_data_tab(data_tab5)
        if data_tab2 or data_tab3 or data_tab4 or data_tab5 or data_tab1:
           something_to_plot = True

        texture_data_tab1 = clean_texture_data(texture_data_tab1)
        print(f"after cleaning data: {texture_data_tab1 = }")

        texture_data_tab2 = clean_texture_data(texture_data_tab2)
        texture_data_tab3 = clean_texture_data(texture_data_tab3)
        texture_data_tab4 = clean_texture_data(texture_data_tab4)
        texture_data_tab5 = clean_texture_data(texture_data_tab5)

        texture_flag_tab1 = boolean_value_of_texture_checklist_to_flag(texture_data_tab1, texture_flag_tab1)
        texture_flag_tab2 = boolean_value_of_texture_checklist_to_flag(texture_data_tab2, texture_flag_tab2)
        texture_flag_tab3 = boolean_value_of_texture_checklist_to_flag(texture_data_tab3, texture_flag_tab3)
        texture_flag_tab4 = boolean_value_of_texture_checklist_to_flag(texture_data_tab4, texture_flag_tab4)
        texture_flag_tab5 = boolean_value_of_texture_checklist_to_flag(texture_data_tab5, texture_flag_tab5)

        grain_size_flag_tab1 = boolean_value_of_grain_size_checklist_to_flag(grain_size_flag_tab1)
        grain_size_flag_tab2 = boolean_value_of_grain_size_checklist_to_flag(grain_size_flag_tab2)
        grain_size_flag_tab3 = boolean_value_of_grain_size_checklist_to_flag(grain_size_flag_tab3)
        grain_size_flag_tab4 = boolean_value_of_grain_size_checklist_to_flag(grain_size_flag_tab4)
        grain_size_flag_tab5 = boolean_value_of_grain_size_checklist_to_flag(grain_size_flag_tab5)

        if no_error_tab1:
            tab1_error_msg = update_xs_dict(xs_dict=xs_dict,
                                            data_tab=data_tab1,
                                            log_label='tab1',
                                            a=a_tab1, b=b_tab1, c=c_tab1,
                                            alpha=alpha_tab1, beta=beta_tab1, gamma=gamma_tab1,
                                            temperature=temperature,
                                            wavelengths_A=wavelengths_A,
                                            texture_flag=texture_flag_tab1,
                                            texture_data=texture_data_tab1,
                                            grain_size_flag=grain_size_flag_tab1,
                                            grain_size=grain_size_tab1,
                                            )
            if tab1_error_msg:
                return None, False, {'display': 'none'}, [html.H4("Error report:"),
                                                          html.Div(f" - Tab1: {tab1_error_msg}")]

        if no_error_tab2:
            tab2_error_msg = update_xs_dict(xs_dict=xs_dict,
                                            data_tab=data_tab2,
                                            log_label='tab2',
                                            a=a_tab2, b=b_tab2, c=c_tab2,
                                            alpha=alpha_tab2, beta=beta_tab2, gamma=gamma_tab2,
                                            temperature=temperature,
                                            wavelengths_A=wavelengths_A,
                                            texture_flag=texture_flag_tab2,
                                            texture_data=texture_data_tab2,
                                            grain_size_flag=grain_size_flag_tab2,
                                            grain_size=grain_size_tab2,
                                            )
            if tab2_error_msg:
                return None, False, {'display': 'none'}, [html.H4("Error report:"),
                                                          html.Div(f" - Tab2: {tab2_error_msg}")]

        if no_error_tab3:
            tab3_error_msg = update_xs_dict(xs_dict=xs_dict,
                                            data_tab=data_tab3,
                                            log_label='tab3',
                                            a=a_tab3, b=b_tab3, c=c_tab3,
                                            alpha=alpha_tab3, beta=beta_tab3, gamma=gamma_tab3,
                                            temperature=temperature,
                                            wavelengths_A=wavelengths_A,
                                            texture_flag=texture_flag_tab3,
                                            texture_data=texture_data_tab3,
                                            grain_size_flag=grain_size_flag_tab3,
                                            grain_size=grain_size_tab3,
                                            )
            if tab3_error_msg:
                return None, False, {'display': 'none'}, [html.H4("Error report:"),
                                                          html.Div(f" - Tab3: {tab3_error_msg}")]

        if no_error_tab4:
            tab4_error_msg = update_xs_dict(xs_dict=xs_dict,
                                            data_tab=data_tab4,
                                            log_label='tab4',
                                            a=a_tab4, b=b_tab4, c=c_tab4,
                                            alpha=alpha_tab4, beta=beta_tab4, gamma=gamma_tab4,
                                            temperature=temperature,
                                            wavelengths_A=wavelengths_A,
                                            texture_flag=texture_flag_tab4,
                                            texture_data=texture_data_tab4,
                                            grain_size_flag=grain_size_flag_tab4,
                                            grain_size=grain_size_tab4,
                                            )
            if tab4_error_msg:
                return None, False, {'display': 'none'}, [html.H4("Error report:"),
                                                          html.Div(f" - Tab4: {tab4_error_msg}")]

        if no_error_tab5:
            tab5_error_msg = update_xs_dict(xs_dict=xs_dict,
                                            data_tab=data_tab5,
                                            log_label='tab5',
                                            a=a_tab5, b=b_tab5, c=c_tab5,
                                            alpha=alpha_tab5, beta=beta_tab5, gamma=gamma_tab5,
                                            temperature=temperature,
                                            wavelengths_A=wavelengths_A,
                                            texture_flag=texture_flag_tab5,
                                            texture_data=texture_data_tab5,
                                            grain_size_flag=grain_size_flag_tab5,
                                            grain_size=grain_size_tab5,
                                            )
            if tab5_error_msg:
                return None, False, {'display': 'none'}, [html.H4("Error report:"),
                                                          html.Div(f" - Tab5: {tab5_error_msg}")]

        if not something_to_plot:
            return None,  False, {'display': 'none'}, None

        df_y = pd.DataFrame.from_dict(xs_dict)
        df_x = pd.DataFrame()
        df_x[constants.energy_name] = ir_util.angstroms_to_ev(wavelengths_A)
        df_x = fill_df_x_types(df=df_x, distance_m=distance, delay_us=delay)

        datasets = {
                    'x': df_x.to_json(orient='split', date_format='iso'),
                    'y': df_y.to_json(orient='split', date_format='iso'),
                    }
        return json.dumps(datasets), True, {'display': 'block'}, None
    else:
        return None,  False, {'display': 'none'}, None


@app.callback(
    [
        Output(app_id_dict['plot_div_id'], 'children'),
        Output(app_id_dict['hidden_df_export_json_id'], 'children'),
        Output(app_id_dict['export_all_button_div_id'], 'children')
    ],
    [
        Input(app_id_dict['hidden_df_json_id'], 'children'),
        Input(app_id_dict['no_error_id'], 'children'),
        Input('x_type', 'value'),
        Input('y_type', 'value'),
        Input('plot_scale', 'value'),
        Input('xs_type', 'value'),
    ],
    )
def plot(jsonified_data, test_passed, x_type, y_type, plot_scale, xs_type):

    if test_passed:

        if jsonified_data is not None:
            df_dict = load_dfs(jsonified_data=jsonified_data)
            df_x = df_dict['x']
            df_y = df_dict['y']

            # Form selected Y df
            to_plot_list = []

            update_list_to_plot(name='tab1', df_y=df_y, to_plot_list=to_plot_list, xs_type=xs_type)
            update_list_to_plot(name='tab2', df_y=df_y, to_plot_list=to_plot_list, xs_type=xs_type)
            update_list_to_plot(name='tab3', df_y=df_y, to_plot_list=to_plot_list, xs_type=xs_type)
            update_list_to_plot(name='tab4', df_y=df_y, to_plot_list=to_plot_list, xs_type=xs_type)
            update_list_to_plot(name='tab5', df_y=df_y, to_plot_list=to_plot_list, xs_type=xs_type)

            try:
                df_to_plot = df_y[to_plot_list]
            except KeyError:
                return resubmit, [None], [None]

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
                                       id=app_id_dict['plot_fig_id']),
                             ]), \
                   [json.dumps(jsonized_plot_df)], \
                   html.Div([html.Button('Export all data as ASCII',
                             id=app_id_dict['export_all_button_id'],
                             style={'width': '100%'})])
        else:
            return plot_loading, [None], [None]
    else:
        return plot_loading, [None], [None]


@app.callback(
    [
        Output(app_id_dict['df_export_tb_div'], 'children'),
    ],
    [
        Input(app_id_dict['display_plot_data_id'], 'value'),
        Input(app_id_dict['hidden_df_export_json_id'], 'children'),
    ],
    [
        State(app_id_dict['no_error_id'], 'children'),
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


# hourglass icon
@app.callback(Output("loading-output-2", 'children'),
              Input(app_id_dict['submit_button_id'], "n_clicks"))
def loading_icon(value):
    time.sleep(3)
    return value


# export all button
@app.callback([Output(app_id_dict['output_of_export_all_button_id'], "children"),
               Output(app_id_dict["download_all_data"], "data")],
              Input(app_id_dict['export_all_button_id'], "n_clicks"),
              State(app_id_dict['hidden_df_json_id'], 'children'),
              )
def export_all(n_clicks, jsonified_data):

    if n_clicks is None:
        return None, None

    print("Exporting all data!")

    if jsonified_data is not None:
        df_dict = load_dfs(jsonified_data=jsonified_data)

    import pprint
    pprint.pprint(f"{df_dict}")

    # _dict  = dict(hidden_df_json)

    # dataset = json.loads(hidden_df_json)
    # df_to_export = pd.read_json(dataset, orient='split')

    # import pprint
    # pprint.pprint(df_to_export)


    # return dict(content=jsonized_plot_df,
#             filename="test_json.txt")


    return None, None,