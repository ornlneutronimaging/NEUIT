import pandas as pd

import callbacks.utilities.constants as constants


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
