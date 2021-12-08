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
