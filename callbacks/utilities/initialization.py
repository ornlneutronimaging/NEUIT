from dash import dash_table as dt
import pandas as pd
import dash_bootstrap_components as dbc

from config import app_info_markdown_dict
from callbacks.utilities.constants import *
from ImagingReso.resonance import Resonance

distance_default = 16.45  # in meter
delay_default = 0  # in us
temperature_default = 293  # in Kelvin
plot_loading = html.H2('Plot loading...')

col_width_1 = 'one column'
col_width_3 = 'three columns'
col_width_5 = 'five columns'
col_width_6 = 'six columns'
empty_div = html.Div()

output_tb_uneven_6_col = [
    {'if': {'column_id': thick_name},
     'width': '22%'},
    {'if': {'column_id': density_name},
     'width': '22%'},
    {'if': {'column_id': ratio_name},
     'width': '22%'},
    {'if': {'column_id': molar_name},
     'width': '11%'},
    {'if': {'column_id': number_density_name},
     'width': '11%'},
    {'if': {'column_id': mu_per_cm_name},
     'width': '11%'},
]

output_stack_header_df = pd.DataFrame({
    'name': [thick_name,
             density_name,
             ratio_name,
             molar_name,
             number_density_name,
             mu_per_cm_name],
    'id': [thick_name,
           density_name,
           ratio_name,
           molar_name,
           number_density_name,
           mu_per_cm_name],
    'deletable': [False, False, False, False, False, False],
    'editable': [False, False, False, False, False, False],
})

output_stack_header_short_df = pd.DataFrame({
    'name': [ratio_name,
             molar_name],
    'id': [ratio_name,
           molar_name],
    'deletable': [False, False],
    'editable': [False, False],
})

iso_tb_header_df = pd.DataFrame({
    'name': [layer_name,
             ele_name,
             iso_name,
             iso_ratio_name],
    'id': [layer_name,
           ele_name,
           iso_name,
           iso_ratio_name],
    'deletable': [False, False, False, False],
    'editable': [False, False, False, True],
    'type': ['any', 'any', 'any', 'numeric']
})

iso_tb_df_default = pd.DataFrame({
    layer_name: [None],
    ele_name: [None],
    iso_name: [None],
    iso_ratio_name: [None],
})

range_tb_even_5_col = [
    {'if': {'column_id': energy_name},
     'width': '20%'},
    {'if': {'column_id': wave_name},
     'width': '20%'},
    {'if': {'column_id': speed_name},
     'width': '20%'},
    {'if': {'column_id': tof_name},
     'width': '20%'},
    {'if': {'column_id': class_name},
     'width': '20%'},
]

sample_tb_even_3_col = [
    {'if': {'column_id': chem_name},
     'width': '33%'},
    {'if': {'column_id': thick_name},
     'width': '33%'},
    {'if': {'column_id': density_name},
     'width': '33%'},
]

iso_tb_even_4_col = [
    {'if': {'column_id': layer_name},
     'width': '25%'},
    {'if': {'column_id': ele_name},
     'width': '25%'},
    {'if': {'column_id': iso_name},
     'width': '25%'},
    {'if': {'column_id': iso_ratio_name},
     'width': '25%'},
]

color = 'rgb(240, 240, 240)'
iso_tb_gray_cols = [
    {'if': {'column_id': layer_name},
     'backgroundColor': color},
    {'if': {'column_id': ele_name},
     'backgroundColor': color},
    {'if': {'column_id': iso_name},
     'backgroundColor': color},
    # striped_rows,
]

# Layout
striped_rows = {'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'}

editable_white = {'if': {'column_editable': False},
                  'backgroundColor': 'rgb(30, 30, 30)',
                  'color': 'white'}

range_tb_gray_cols = [
    {'if': {'column_id': speed_name},
     'backgroundColor': color},
    {'if': {'column_id': tof_name},
     'backgroundColor': color},
    {'if': {'column_id': class_name},
     'backgroundColor': color},
]


def init_app_ids(app_name: str):
    id_dict = {}
    id_dict['more_about_app_id'] = app_name + '_more_about_app'
    id_dict['app_info_id'] = app_name + '_app_info'
    id_dict['sample_upload_id'] = app_name + '_sample_upload'
    id_dict['error_upload_id'] = app_name + '_error_upload'
    id_dict['hidden_upload_time_id'] = app_name + '_time_upload'
    id_dict['add_row_id'] = app_name + '_add_row'
    id_dict['del_row_id'] = app_name + '_del_row'
    id_dict['database_id'] = app_name + '_database'
    id_dict['sample_table_id'] = app_name + '_sample_table'
    id_dict['iso_check_id'] = app_name + '_iso_check'
    id_dict['iso_div_id'] = app_name + '_iso_input'
    id_dict['iso_table_id'] = app_name + '_iso_table'
    id_dict['submit_button_id'] = app_name + '_submit'
    id_dict['result_id'] = app_name + '_result'
    id_dict['error_id'] = app_name + '_error'
    id_dict['output_id'] = app_name + '_output'

    if app_name == 'transmission':  # id names for neutron transmission only
        id_dict['beamline_id'] = app_name + '_beamline'
        id_dict['band_div_id'] = app_name + '_band_div'
        id_dict['band_min_id'] = app_name + '_band_min'
        id_dict['band_max_id'] = app_name + '_band_max'
        id_dict['band_type_id'] = app_name + '_band_type'
        id_dict['band_unit_id'] = app_name + '_band_unit'

    elif app_name == 'resonance':  # id names for neutron resonance only
        id_dict['slider_id'] = app_name + '_e_range_slider'
        id_dict['range_table_id'] = app_name + '_range_table'
        id_dict['e_step_id'] = app_name + '_e_step'
        id_dict['distance_id'] = app_name + '_distance'
        id_dict['hidden_prev_distance_id'] = app_name + '_hidden_prev_distance'
        id_dict['hidden_range_input_coord_id'] = app_name + '_hidden_range_input_coord'
        id_dict['hidden_df_export_json_id'] = app_name + '_hidden_df_export_json'
        id_dict['hidden_df_json_id'] = app_name + '_hidden_df_json'
        id_dict['df_export_tb_div'] = app_name + '_df_export_tb_div'
        id_dict['df_export_tb'] = app_name + '_df_export_tb'
        id_dict['plot_div_id'] = app_name + '_plot'
        id_dict['plot_fig_id'] = app_name + '_plot_fig'
        id_dict['plot_options_div_id'] = app_name + '_plot_options'
        id_dict['display_plot_data_id'] = app_name + '_display_plot_data'
        id_dict['prev_x_type_id'] = app_name + '_prev_x_type'

    elif app_name == 'converter':  # id names for composition converter only
        id_dict['compos_type_id'] = app_name + '_compos_input_type'

    elif app_name == 'tof_plotter':  # id names for TOF plotter only
        id_dict['distance_id'] = app_name + '_distance'
        id_dict['delay_id'] = app_name + '_delay'
        id_dict['spectra_upload_id'] = app_name + '_spectra'
        id_dict['spectra_upload_fb_id'] = app_name + '_spectra_fb'
        id_dict['data_upload_id'] = app_name + '_data'
        id_dict['data_upload_fb_id'] = app_name + '_data_fb'
        id_dict['background_upload_id'] = app_name + '_background'
        id_dict['background_check_id'] = app_name + '_background_ck'
        id_dict['background_upload_fb_id'] = app_name + '_background_fb'
        id_dict['plot_div_id'] = app_name + '_plot'
        id_dict['plot_fig_id'] = app_name + '_plot_fig'

    elif app_name == 'bragg':  # id names for bragg edge simulator only
        id_dict['error_id2'] = app_name + '_error2'
        id_dict['temperature_id'] = app_name + '_temperature'
        id_dict['distance_id'] = app_name + '_distance'
        id_dict['band_min_id'] = app_name + '_band_min'
        id_dict['band_max_id'] = app_name + '_band_max'
        id_dict['band_step_id'] = app_name + '_band_step'
        id_dict['band_unit_id'] = app_name + '_band_unit'
        id_dict['cif_upload_id'] = app_name + '_cif'
        id_dict['cif_upload_fb_id'] = app_name + '_cif_fb'
        id_dict['hidden_df_json_id'] = app_name + '_hidden_df_json'
        id_dict['hidden_df_export_json_id'] = app_name + '_hidden_df_export_json'
        id_dict['df_export_tb_div'] = app_name + '_df_export_tb_div'
        id_dict['df_export_tb'] = app_name + '_df_export_tb'
        id_dict['plot_div_id'] = app_name + '_plot'
        id_dict['plot_fig_id'] = app_name + '_plot_fig'
        id_dict['display_plot_data_id'] = app_name + '_display_plot_data'

    return id_dict


# def init_app_links(current_app, app_dict_all):
#     links_div_list = [html.A('Home', href='/', target="_blank")]
#     for _each_app in app_dict_all.keys():
#         if current_app != _each_app:
#             links_div_list.append(html.Br())
#             links_div_list.append(html.A(app_dict[_each_app]['name'],
#                                          href=app_dict[_each_app]['url'],
#                                          target="_blank"))
#     links_div_list.append(html.H1(app_dict[current_app]['name']))
#     return html.Div(links_div_list)

def init_app_about(current_app, app_id_dict):
    more_info_check = dcc.Checklist(
        id=app_id_dict['more_about_app_id'],
        options=[
            {'label': 'More about this app \U0001F4AC', 'value': 'more'},
        ],
        value=[],
        labelStyle={'display': 'inline-block'}
    )

    more_info_div = html.Div(
        [
            app_info_markdown_dict[current_app],
        ],
        id=app_id_dict['app_info_id'],
        style={'display': 'none'},
    )

    return html.Div([more_info_check, more_info_div])


def init_upload_field(id_str: str, div_str: str, hidden_div_str: str, add_row_id: str, del_row_id: str,
                      database_id: str, app_id: str):
    if app_id == 'converter':
        _compos_type_div = html.Div(
            [
                html.H6('Composition input type:'),
                dcc.RadioItems(id=app_id + '_compos_input_type',
                               options=[
                                   {'label': weight_name, 'value': weight_name},
                                   {'label': atomic_name, 'value': atomic_name},
                               ],
                               value=weight_name,
                               # labelStyle={'display': 'inline-block'},
                               ),
            ], className='row',
        )
        _nuclear_database_div_style = {'display': 'none'}
    else:
        _compos_type_div = None
        _nuclear_database_div_style = {'display': 'block'}

    # Upload div
    upload_field = html.Div(
        [
            # Database dropdown
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H6('Nuclear database:'),
                                    dcc.Dropdown(
                                        id=database_id,
                                        options=[
                                            {'label': 'ENDF/B-VII.1', 'value': 'ENDF_VII'},
                                            {'label': 'ENDF/B-VIII.0', 'value': 'ENDF_VIII'},
                                        ],
                                        value='ENDF_VIII',
                                        searchable=False,
                                        clearable=False,
                                    ),
                                ], width=4
                            )
                        ]
                    ),
                ], style=_nuclear_database_div_style,
            ),
            _compos_type_div,
            # Sample input
            dbc.Row([html.H3('Sample info')]),
            dcc.Upload(id=id_str,
                       children=html.Div(
                           [
                               'Drag and Drop or ',
                               html.A('Select Files'),
                               " (previously exported '###.csv')",
                           ],
                       ),
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
            html.Div(id=div_str),
            html.Div(id=hidden_div_str, style={'display': 'none'}, children=0),
            html.Button('+', id=add_row_id, n_clicks_timestamp=0),
            html.Button('-', id=del_row_id, n_clicks_timestamp=0),
        ])
    return upload_field


def init_iso_table(id_str: str):
    iso_table = dt.DataTable(
        data=iso_tb_df_default.to_dict('records'),
        columns=iso_tb_header_df.to_dict('records'),
        # editable=True,
        row_selectable=False,
        filter_action='none',
        sort_action='none',
        row_deletable=False,
        # export_format='csv',
        style_cell_conditional=iso_tb_even_4_col,
        style_data_conditional=iso_tb_gray_cols,
        fixed_rows={'headers': True, 'data': 0},
        style_table={
            'maxHeight': '300',
            'overflowY': 'scroll'
        },
        id=id_str
    )
    return iso_table


def init_reso_from_tb(range_tb_df, e_step, database):
    v_1 = range_tb_df[energy_name][0]
    v_2 = range_tb_df[energy_name][1]
    if v_1 < v_2:
        o_reso = Resonance(energy_min=v_1, energy_max=v_2, energy_step=e_step, database=database)
    else:
        o_reso = Resonance(energy_min=v_2, energy_max=v_1, energy_step=e_step, database=database)
    return o_reso
