from dash.dependencies import Input, Output, State
import matplotlib.pyplot as plt
from bem import xscalc

from app import app
from callbacks.utilities._utilities import *

from callbacks.utilities.initialization import init_app_ids

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
        Input(app_id_dict['error_id2'], 'children'),
    ])
def show_output_div(n_submit, test_passed, error_in_bem):
    if n_submit is not None:
        if test_passed and error_in_bem is True:
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    else:
        return {'display': 'none'}


@app.callback(
    [
        Output(app_id_dict['hidden_df_json_id'], 'children'),
        Output(app_id_dict['error_id2'], 'children'),
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
        error_div_list = []
        xs_dict = {}
        wavelengths_A = np.arange(band_min, band_max, band_step)
        if cif_uploads is not None:
            for each_index, each_content in enumerate(cif_uploads):
                _cif_struc = parse_cif_upload(content=each_content)
                _name_only = cif_names[each_index].split('.')[0]
                print("'{}', calculating cross-sections...".format(cif_names[each_index]))
                try:
                    xscalculator = xscalc.XSCalculator(_cif_struc, temperature_K, max_diffraction_index=4)
                    xs_dict[_name_only + ' (total)'] = xscalculator.xs(wavelengths_A)
                    xs_dict[_name_only + ' (abs)'] = xscalculator.xs_abs(wavelengths_A)
                    xs_dict[_name_only + ' (coh el)'] = xscalculator.xs_coh_el(wavelengths_A)
                    xs_dict[_name_only + ' (inc el)'] = xscalculator.xs_inc_el(wavelengths_A)
                    xs_dict[_name_only + ' (coh inel)'] = xscalculator.xs_coh_inel(wavelengths_A)
                    xs_dict[_name_only + ' (inc inel)'] = xscalculator.xs_inc_inel(wavelengths_A)
                    print("Calculation done.")
                except ValueError as error_msg:
                    error = "ERROR: '{}', ".format(cif_names[each_index]) + str(error_msg).split('.')[0] + '.'
                    error_div_list.append(error)
            if len(error_div_list) == 0:
                df_y = pd.DataFrame.from_dict(xs_dict)
                df_x = pd.DataFrame()
                df_x[wave_name] = wavelengths_A
                df_x[energy_name] = ir_util.angstroms_to_ev(wavelengths_A)
                datasets = {
                    'x': df_x.to_json(orient='split', date_format='iso'),
                    'y': df_y.to_json(orient='split', date_format='iso'),
                }
                return json.dumps(datasets), True
            else:
                return None, error_div_list
        else:
            return None, False
    else:
        return None, False

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
    if test_passed:
        if jsonified_data is not None:
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
                if 'coh_el' in xs_type:
                    to_plot_list.append(_name_only + ' (coh el)')
                if 'coh_inel' in xs_type:
                    to_plot_list.append(_name_only + ' (coh inel)')
                if 'inc_el' in xs_type:
                    to_plot_list.append(_name_only + ' (inc el)')
                if 'inc_inel' in xs_type:
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
