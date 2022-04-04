import pandas as pd
import numpy as np

import ImagingReso._utilities as ir_util

from callbacks.utilities.constants import *
from callbacks.utilities.validator import is_number
from callbacks.utilities.all_apps import (load_dfs, y_type_to_y_label, x_type_to_x_tag)


energy_range_header_df = pd.DataFrame({
    'name': [energy_name,
             wave_name,
             speed_name,
             tof_name,
             class_name],
    'id': [energy_name,
           wave_name,
           speed_name,
           tof_name,
           class_name],
    'deletable': [False, False, False, False, False],
    'editable': [True, True, False, False, False],
    'type': ['numeric', 'numeric', 'any', 'any', 'any']
})


def classify_neutron(energy_ev):
    assert energy_ev >= 0
    e = energy_ev
    if 0 < e <= 2.5e-7:
        return 'Ultra-cold'
    elif 2.5e-7 < e < 0.025:
        return 'Cold'
    elif 0.025 <= e <= 0.2:
        return 'Thermal'
    elif 0.2 < e < 900:
        return 'Epithermal'
    elif 900 < e <= 0.5e6:
        return 'Intermediate'
    elif 0.5e6 < e <= 20e6:
        return 'Fast'
    elif 20e6 < e:
        return 'Ultra-fast'


def fill_range_table_by_e(e_ev, distance_m):
    _e = e_ev
    _lambda = round(ir_util.ev_to_angstroms(array=_e), 5)
    _v = round(3956. / np.sqrt(81.787 / (_e * 1000.)), 2)
    _tof = round(ir_util.ev_to_s(array=_e, source_to_detector_m=distance_m, offset_us=0) * 1e6, 4)
    _class = classify_neutron(_e)
    return {energy_name: _e,
            wave_name: _lambda,
            speed_name: _v,
            tof_name: _tof,
            class_name: _class}


def fill_range_table_by_wave(wave_angstroms, distance_m):
    _lambda = wave_angstroms
    _e = round(ir_util.angstroms_to_ev(array=_lambda), 5)
    _v = round(3956. / np.sqrt(81.787 / (_e * 1000.)), 2)
    _tof = round(ir_util.ev_to_s(array=_e, source_to_detector_m=distance_m, offset_us=0) * 1e6, 4)
    _class = classify_neutron(_e)
    return {energy_name: _e,
            wave_name: _lambda,
            speed_name: _v,
            tof_name: _tof,
            class_name: _class}


def update_range_tb_by_coordinate(range_table_rows, distance, modified_coord):
    row = modified_coord[0]
    col = modified_coord[1]
    if col == 0:
        input_value = range_table_rows[row][energy_name]
        if is_number(input_value) and float(input_value) > 0:
            things_to_fill = fill_range_table_by_e(e_ev=float(input_value), distance_m=distance)
            for each_col in range_table_rows[row].keys():
                range_table_rows[row][each_col] = things_to_fill[each_col]
        else:
            for each_col in [wave_name, speed_name, tof_name, class_name]:
                range_table_rows[row][each_col] = 'N/A'
    elif col == 1:  # Changed back to 1 from 4 after updating to pandas>=0.25.0
        input_value = range_table_rows[row][wave_name]
        if is_number(input_value) and float(input_value) > 0:
            things_to_fill = fill_range_table_by_wave(wave_angstroms=float(input_value), distance_m=distance)
            for each_col in range_table_rows[row].keys():
                range_table_rows[row][each_col] = things_to_fill[each_col]
        else:
            for each_col in [energy_name, speed_name, tof_name, class_name]:
                range_table_rows[row][each_col] = 'N/A'

    return range_table_rows


def shape_reso_df_to_output(y_type, x_type, show_opt, jsonified_data, prev_show_opt, to_csv):
    df_dict = load_dfs(jsonified_data=jsonified_data)
    # Determine Y df and y_label to plot

    y_label = y_type_to_y_label(y_type)

    df_x = df_dict['x']
    df_y = df_dict['y']

    # Determine X names to plot
    x_tag = x_type_to_x_tag(x_type)

    # Locate items based on plot level provided
    total_col_name_list = []
    layer_col_name_list = []
    ele_col_name_list = []
    iso_col_name_list = []
    atoms_per_cm3_col_name_list = []
    for col_name in df_y.columns:
        if col_name.count('Total') == 0:
            _num_of_slash = col_name.count('/')
            if _num_of_slash == 0:
                layer_col_name_list.append(col_name)
            elif _num_of_slash == 1:
                ele_col_name_list.append(col_name)
            elif _num_of_slash == 2:
                if col_name.count('atoms_per_cm3') != 0:
                    atoms_per_cm3_col_name_list.append(col_name)
                else:
                    iso_col_name_list.append(col_name)
        else:
            total_col_name_list.append(col_name)

    _to_export_list = []
    if len(show_opt) == 0:
        _to_export_list.append(prev_show_opt)
    if 'total' in show_opt:
        _to_export_list.extend(total_col_name_list)
    if 'layer' in show_opt:
        _to_export_list.extend(layer_col_name_list)
    if 'ele' in show_opt:
        _to_export_list.extend(ele_col_name_list)
    if to_csv:
        _to_export_list.extend(atoms_per_cm3_col_name_list)
    if 'iso' in show_opt:
        _to_export_list.extend(iso_col_name_list)

    return df_x, df_y, _to_export_list, x_tag, y_label


def fill_df_x_types(df: pd.DataFrame, distance_m, delay_us):
    df.insert(loc=1, column=tof_name, value=ir_util.ev_to_s(array=df[energy_name],
                                                            source_to_detector_m=distance_m,
                                                            offset_us=delay_us))
    df.insert(loc=1, column=wave_name, value=ir_util.ev_to_angstroms(df[energy_name]))
    df[tof_name] = df[tof_name] * 1e6
    return df
