import pandas as pd

import callbacks.utilities.constants as constants


sample_header_df = pd.DataFrame({
    'name': [constants.chem_name,
             constants.thick_name,
             constants.density_name],
    'id': [constants.chem_name,
           constants.thick_name,
           constants.density_name],
    # 'deletable': [False, False, False],
    # 'editable': [True, True, True],
    'type': ['text', 'numeric', 'any']
})