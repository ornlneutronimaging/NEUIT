import pandas as pd

import callbacks.utilities.constants as constants


compos_header_df = pd.DataFrame({
    'name': [constants.chem_name,
             constants.weight_name],
    'id': [constants.chem_name,
           constants.compos_2nd_col_id],
    # 'deletable': [False, False, False],
    # 'editable': [True, True, True],
    'type': ['text', 'numeric']
})


compos_header_percent_df = pd.DataFrame({
    'name': [constants.chem_name,
             constants.weight_name_p,
             constants.atomic_name_p],
    'id': [constants.chem_name,
           constants.weight_name_p,
           constants.atomic_name_p],
    # 'deletable': [False, False, False],
    'editable': [False, False, False],
})
