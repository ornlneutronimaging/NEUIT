import base64
import pandas as pd
import io

import ImagingReso._utilities as ir_util

from callbacks.utilities.constants import *


def x_type_to_x_label(x_type):
    if x_type == 'energy':
        x_label = energy_name
    elif x_type == 'lambda':
        x_label = wave_name
    elif x_type == 'time':
        x_label = tof_name
    else:  # x_type == 'number':
        x_label = number_name
    return x_label


def shape_df_to_plot(df, x_type, distance, delay):
    if x_type == 'lambda':
        df['X'] = ir_util.s_to_angstroms(array=df['X'], source_to_detector_m=distance, offset_us=delay)
    if x_type == 'energy':
        df['X'] = ir_util.s_to_ev(array=df['X'], source_to_detector_m=distance, offset_us=delay)
    if x_type == 'number':
        df['X'] = range(1, len(df['X']) + 1)
    if x_type == 'time':
        df['X'] = df['X'] * 1e6 + delay
    return df


def parse_content(content, name, header):
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    error_div = None
    if '.csv' in name:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), na_filter=False, header=header)
    elif '.xls' in name:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(io.BytesIO(decoded), na_filter=False, header=header)
    elif '.txt' in name:
        # Assume that the user uploaded an txt file
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t', na_filter=False, header=header)
    else:
        df = None
        error_div = html.Div(
            ["\u274C Type error: '{}' is not supported, only '.csv', '.xls' and '.txt' are currently supported.".format(
                name)])
    return df, error_div
