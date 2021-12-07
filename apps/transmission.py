import dash_bootstrap_components as dbc
from callbacks.transmission import *

sample_df_default = pd.DataFrame({
    chem_name: ['H2O'],
    thick_name: [2],
    density_name: [1],
})

app_name = 'transmission'
app_id_dict = init_app_ids(app_name=app_name)

layout = html.Div(
        [
            dbc.Row([html.H2("Neutron Transmission",
                             style=({'color': 'blue'}),
                             ),
                     ],
                    class_name='title_tools',
            ),
            html.Hr(style={'borderTop': '3px solid blue'}),
            # Beamline selection
            html.Div(
                    [
                        html.Div(
                                [
                                    html.H6('Beam spectrum from:'),
                                    html.Div(
                                            [
                                                dcc.Dropdown(
                                                        id=app_id_dict['beamline_id'],
                                                        options=[
                                                            {'label': 'IMAGING (CG-1D), HFIR', 'value': 'imaging'},
                                                            {'label': u'IMAGING (CG-1D) \u2264 5.35 \u212B, HFIR',
                                                             'value': 'imaging_crop'},
                                                            {'label': 'SNAP (BL-3), SNS', 'value': 'snap'},
                                                            # {'label': 'SNS, VENUS (BL-10)', 'value': 'venus'},
                                                        ],
                                                        value='imaging',
                                                        searchable=False,
                                                        clearable=False,
                                                ),
                                            ]
                                    ),
                                ], className='five columns', style={'verticalAlign': 'middle'},
                        ),
                        html.Div(
                                [
                                    html.Div(
                                            [
                                                html.H6('Band width:',
                                                        className='four columns'
                                                        ),
                                                dcc.RadioItems(id=app_id_dict['band_type_id'],
                                                               options=[
                                                                   {'label': 'Energy (eV)', 'value': 'energy'},
                                                                   {'label': 'Wavelength (\u212B)',
                                                                    'value': 'lambda'},
                                                               ],
                                                               value='lambda',
                                                               className='four columns',
                                                               labelStyle={'display': 'inline-block'},
                                                               ),
                                            ], className='row'
                                    ),
                                    html.Div(
                                            [
                                                dcc.Input(id=app_id_dict['band_min_id'], type='number',
                                                          inputMode='numeric',
                                                          placeholder='Min.',
                                                          step=0.001,
                                                          className='four columns',
                                                          ),
                                                dcc.Input(id=app_id_dict['band_max_id'], type='number',
                                                          inputMode='numeric',
                                                          placeholder='Max.',
                                                          step=0.001,
                                                          className='four columns',
                                                          ),
                                                html.P('\u212B',
                                                       id=app_id_dict['band_unit_id'],
                                                       style={'marginBottom': 10, 'marginTop': 5},
                                                       className='one column',
                                                       ),
                                            ], className='row', style={'verticalAlign': 'middle'},
                                    ),
                                ], className=col_width_6, style={'display': 'none'}, id=app_id_dict['band_div_id'],
                        ),
                    ], className='row',
            ),
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
                                data=sample_df_default.to_dict('records'),
                                # optional - sets the order of columns
                                columns=sample_header_df.to_dict('records'),
                                editable=True,
                                row_selectable=False,
                                filter_action='none',
                                sort_action='none',
                                row_deletable=True,
                                export_format='csv',
                                style_cell_conditional=sample_tb_even_3_col,
                                style_data_conditional=[striped_rows],
                                id=app_id_dict['sample_table_id']
                        ),
                        markdown_sample,
                        label_sample,

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
                        # Transmission at CG-1D and stack info
                        html.Div(id=app_id_dict['result_id']),
                    ],
                    id=app_id_dict['output_id'],
                    style={'display': 'none'},
            ),
        ],
        style={'margin': '25px'}
)
