import dash_bootstrap_components as dbc
from callbacks.converter import *
from callbacks.utilities.initialization import init_app_ids

# Composition converter tool

compos_df_default = pd.DataFrame({
    chem_name: ['B4C', 'SiC'],
    compos_2nd_col_id: ['50', '50'],
})

app_name = 'converter'
app_id_dict = init_app_ids(app_name=app_name)

# Create app layout
layout = html.Div(
    [
        dbc.Row([html.H2("Composition Converter",
                         style=({'color': 'blue'}),
                         ),
                 ],
                class_name='title_tools',
                ),
        html.Hr(style={'borderTop': '3px solid blue'}),

        # Sample input
        html.Div(
            [
                init_upload_field(id_str=app_id_dict['sample_upload_id'],
                                  div_str=app_id_dict['error_upload_id'],
                                  hidden_div_str=app_id_dict['hidden_upload_time_id'],
                                  add_row_id=app_id_dict['add_row_id'],
                                  del_row_id=app_id_dict['del_row_id'],
                                  database_id=app_id_dict['database_id'],
                                  app_id=app_name,
                                  ),
                dt.DataTable(
                    data=compos_df_default.to_dict('records'),
                    # optional - sets the order of columns
                    columns=compos_header_df.to_dict('records'),
                    editable=True,
                    row_selectable=False,
                    filter_action='none',
                    sort_action='none',
                    row_deletable=True,
                    export_format='csv',
                    style_cell_conditional=[
                        {'if': {'column_id': chem_name},
                         'width': '50%'},
                        {'if': {'column_id': compos_2nd_col_id},
                         'width': '50%'},
                    ],
                    style_data_conditional=[striped_rows],
                    id=app_id_dict['sample_table_id']
                ),
                markdown_compos,

                # Input table for isotopic ratios
                dcc.Checklist(id=app_id_dict['iso_check_id'],
                              options=[
                                  {'label': 'Modify isotopic ratios', 'value': 'yes'},
                              ], value=[],
                              ),
                html.Div(
                    [
                        markdown_iso,
                        init_iso_table(id_str=app_id_dict['iso_table_id'])
                    ],
                    id=app_id_dict['iso_div_id'],
                    style={'display': 'none'},
                ),
                html.Button('Submit', id=app_id_dict['submit_button_id']),
            ]
        ),

        # Error message div
        html.Div(id=app_id_dict['error_id'], children=None),

        # Output div
        html.Div(
            [
                # Effective formula and stack info
                html.Div(id=app_id_dict['result_id']),
            ],
            id=app_id_dict['output_id'],
            style={'display': 'none'},
        ),
    ],
    style={'margin': '25px'}
)
