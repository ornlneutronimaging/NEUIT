import os
import sys
from dash import html
from dash import dcc
from dash import dash_table as dt
import pandas as pd
import io
import base64
from scipy.interpolate import interp1d
import numpy as np
import json
import plotly.tools as tls

if sys.version_info[0] < 3:
    from diffpy.Structure.Parsers import getParser
else:
    from diffpy.structure.parsers import getParser

import ImagingReso._utilities as ir_util
from ImagingReso.resonance import Resonance

from config import app_dict
from callbacks.utilities.validator import MyValidator, is_number, validate_input
# from callbacks.utilities import constants
import callbacks.utilities.constants as constants
from callbacks.utilities.initialization import iso_tb_df_default
from callbacks.utilities.resonance import fill_range_table_by_e


col_width_1 = 'one column'
col_width_3 = 'three columns'
col_width_5 = 'five columns'
col_width_6 = 'six columns'
empty_div = html.Div()

# distance_default = 16.45  # in meter
# delay_default = 0  # in us
# temperature_default = 293  # in Kelvin
# plot_loading = html.H2('Plot loading...')


compos_dict_schema = {
    # chem_name: {'type': 'string', 'empty': False, 'required': True, 'is_chem_name': True, },
    constants.chem_name: {'type': 'string', 'empty': False, 'required': True, 'ENDF_VIII': True, },
    constants.compos_2nd_col_id: {'type': 'number', 'greater_than_zero': True},
}

iso_dict_schema = {
    # layer_name: {'type': 'string', 'empty': False, 'required': True, 'is_chem_name': True, },
    constants.layer_name: {'type': 'string', 'empty': False, 'required': True, 'ENDF_VIII': True, },
    constants.ele_name: {'type': 'string', 'empty': False, 'required': True, },
    constants.iso_name: {'type': 'string', 'empty': False, 'required': True, },
    constants.iso_ratio_name: {'type': 'number', 'min': 0, 'max': 1, 'required': True, 'between_zero_and_one': True, },
}

sample_dict_schema = {
    # chem_name: {'type': 'string', 'empty': False, 'required': True, 'is_chem_name': True, },
    constants.chem_name: {'type': 'string', 'empty': False, 'required': True, 'ENDF_VIII': True, },
    constants.thick_name: {'type': 'number', 'min': 0, 'required': True, },
    constants.density_name: {'anyof_type': ['string', 'number'], 'min': 0, 'empty_str': True, },
}


# def shape_reso_df_to_output(y_type, x_type, show_opt, jsonified_data, prev_show_opt, to_csv):
#     df_dict = load_dfs(jsonified_data=jsonified_data)
#     # Determine Y df and y_label to plot
#
#     y_label = y_type_to_y_label(y_type)
#
#     df_x = df_dict['x']
#     df_y = df_dict['y']
#
#     # Determine X names to plot
#     x_tag = x_type_to_x_tag(x_type)
#
#     # Locate items based on plot level provided
#     total_col_name_list = []
#     layer_col_name_list = []
#     ele_col_name_list = []
#     iso_col_name_list = []
#     atoms_per_cm3_col_name_list = []
#     for col_name in df_y.columns:
#         if col_name.count('Total') == 0:
#             _num_of_slash = col_name.count('/')
#             if _num_of_slash == 0:
#                 layer_col_name_list.append(col_name)
#             elif _num_of_slash == 1:
#                 ele_col_name_list.append(col_name)
#             elif _num_of_slash == 2:
#                 if col_name.count('atoms_per_cm3') != 0:
#                     atoms_per_cm3_col_name_list.append(col_name)
#                 else:
#                     iso_col_name_list.append(col_name)
#         else:
#             total_col_name_list.append(col_name)
#
#     _to_export_list = []
#     if len(show_opt) == 0:
#         _to_export_list.append(prev_show_opt)
#     if 'total' in show_opt:
#         _to_export_list.extend(total_col_name_list)
#     if 'layer' in show_opt:
#         _to_export_list.extend(layer_col_name_list)
#     if 'ele' in show_opt:
#         _to_export_list.extend(ele_col_name_list)
#     if to_csv:
#         _to_export_list.extend(atoms_per_cm3_col_name_list)
#     if 'iso' in show_opt:
#         _to_export_list.extend(iso_col_name_list)
#
#     return df_x, df_y, _to_export_list, x_tag, y_label


# def fill_df_x_types(df: pd.DataFrame, distance_m):
#     df.insert(loc=1, column=constants.tof_name, value=ir_util.ev_to_s(array=df[constants.energy_name],
#                                                             source_to_detector_m=distance_m,
#                                                             offset_us=0))
#     df.insert(loc=1, column=constants.wave_name, value=ir_util.ev_to_angstroms(df[constants.energy_name]))
#     df[constants.tof_name] = df[constants.tof_name] * 1e6
#     return df


# def shape_df_to_plot(df, x_type, distance, delay):
#     if x_type == 'lambda':
#         df['X'] = ir_util.s_to_angstroms(array=df['X'], source_to_detector_m=distance, offset_us=delay)
#     if x_type == 'energy':
#         df['X'] = ir_util.s_to_ev(array=df['X'], source_to_detector_m=distance, offset_us=delay)
#     if x_type == 'number':
#         df['X'] = range(1, len(df['X']) + 1)
#     if x_type == 'time':
#         df['X'] = df['X'] * 1e6 + delay
#     return df


# # Layout
# striped_rows = {'if': {'row_index': 'odd'},
#                 'backgroundColor': 'rgb(248, 248, 248)'}
#
# editable_white = {'if': {'column_editable': False},
#                   'backgroundColor': 'rgb(30, 30, 30)',
#                   'color': 'white'}


# def parse_content(content, name, header):
#     content_type, content_string = content.split(',')
#     decoded = base64.b64decode(content_string)
#     error_div = None
#     if '.csv' in name:
#         # Assume that the user uploaded a CSV file
#         df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), na_filter=False, header=header)
#     elif '.xls' in name:
#         # Assume that the user uploaded an excel file
#         df = pd.read_excel(io.BytesIO(decoded), na_filter=False, header=header)
#     elif '.txt' in name:
#         # Assume that the user uploaded an txt file
#         df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t', na_filter=False, header=header)
#     else:
#         df = None
#         error_div = html.Div(
#             ["\u274C Type error: '{}' is not supported, only '.csv', '.xls' and '.txt' are currently supported.".format(
#                 name)])
#     return df, error_div


# def parse_cif_upload(content):
#     content_type, content_string = content.split(',')
#     decoded = base64.b64decode(content_string)
#
#     cif_s = decoded.decode('utf-8')
#     p = getParser('cif')
#     struc = p.parse(cif_s)
#     struc.sg = p.spacegroup
#     return struc


# app_links_list = []
# for i, each_app in enumerate(app_dict.keys()):
#     current_number_str = str(i + 1) + '. '
#     current_app_name = app_dict[each_app]['name']
#     current_url = app_dict[each_app]['url']
#     app_links_list.append(current_number_str)
#     app_links_list.append(dcc.Link(current_app_name, href=current_url))
#     app_links_list.append(html.Br())
# app_links_div = html.Div(app_links_list)


# output_tb_uneven_6_col = [
#     {'if': {'column_id': constants.thick_name},
#      'width': '22%'},
#     {'if': {'column_id': constants.density_name},
#      'width': '22%'},
#     {'if': {'column_id': constants.ratio_name},
#      'width': '22%'},
#     {'if': {'column_id': constants.molar_name},
#      'width': '11%'},
#     {'if': {'column_id': constants.number_density_name},
#      'width': '11%'},
#     {'if': {'column_id': constants.mu_per_cm_name},
#      'width': '11%'},
# ]
