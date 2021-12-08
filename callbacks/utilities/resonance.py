import pandas as pd
import numpy as np

import ImagingReso._utilities as ir_util

import callbacks.utilities.constants as constants
from callbacks.utilities.validator import is_number


energy_range_header_df = pd.DataFrame({
    'name': [constants.energy_name,
             constants.wave_name,
             constants.speed_name,
             constants.tof_name,
             constants.class_name],
    'id': [constants.energy_name,
           constants.wave_name, constants.speed_name,
           constants.tof_name,
           constants.class_name],
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
    return {constants.energy_name: _e,
            constants.wave_name: _lambda,
            constants.speed_name: _v,
            constants.tof_name: _tof,
            constants.class_name: _class}


def fill_range_table_by_wave(wave_angstroms, distance_m):
    _lambda = wave_angstroms
    _e = round(ir_util.angstroms_to_ev(array=_lambda), 5)
    _v = round(3956. / np.sqrt(81.787 / (_e * 1000.)), 2)
    _tof = round(ir_util.ev_to_s(array=_e, source_to_detector_m=distance_m, offset_us=0) * 1e6, 4)
    _class = classify_neutron(_e)
    return {constants.energy_name: _e,
            constants.wave_name: _lambda,
            constants.speed_name: _v,
            constants.tof_name: _tof,
            constants.class_name: _class}


def update_range_tb_by_coordinate(range_table_rows, distance, modified_coord):
    row = modified_coord[0]
    col = modified_coord[1]
    if col == 0:
        input_value = range_table_rows[row][constants.energy_name]
        if is_number(input_value) and float(input_value) > 0:
            things_to_fill = fill_range_table_by_e(e_ev=float(input_value), distance_m=distance)
            for each_col in range_table_rows[row].keys():
                range_table_rows[row][each_col] = things_to_fill[each_col]
        else:
            for each_col in [constants.wave_name, constants.speed_name, constants.tof_name, constants.class_name]:
                range_table_rows[row][each_col] = 'N/A'
    elif col == 1:  # Changed back to 1 from 4 after updating to pandas>=0.25.0
        input_value = range_table_rows[row][constants.wave_name]
        if is_number(input_value) and float(input_value) > 0:
            things_to_fill = fill_range_table_by_wave(wave_angstroms=float(input_value), distance_m=distance)
            for each_col in range_table_rows[row].keys():
                range_table_rows[row][each_col] = things_to_fill[each_col]
        else:
            for each_col in [constants.energy_name, constants.speed_name, constants.tof_name, constants.class_name]:
                range_table_rows[row][each_col] = 'N/A'

    return range_table_rows