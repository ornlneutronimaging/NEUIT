import dash_bootstrap_components as dbc

from callbacks.bragg import *
from callbacks.utilities.constants import *
from callbacks.utilities.initialization import (init_app_ids, temperature_default, distance_default, delay_default,
                                                init_app_about, init_display_plot_data_check, sample_tb_even_4_col)
from callbacks.utilities.plot import bragg_plot_option_div
from callbacks.utilities.all_apps import bragg_sample_header_df

# Bragg-edge tool

app_name = 'bragg'
app_id_dict = init_app_ids(app_name=app_name)

# bragg_sample_df_default = pd.DataFrame({
#     chem_name: ['Ni'],
#     index_number_h: [0.0],
#     index_number_k: [0.0],
#     index_number_l: [0.0],
#     axial_length_a: [3.5238],
#     axial_length_b: [3.5238],
#     axial_length_c: [3.5238],
#     interaxial_angle_alpha: [90],
#     interaxial_angle_beta: [90],
#     interaxial_angle_gamma: [90]
# })


bragg_sample_df_default = pd.DataFrame({
    chem_name: [],
    index_number_h: [],
    index_number_k: [],
    index_number_l: [],
})


def tab_content(upload_id=None,
                add_row_id=None,
                data_table=None,
                cif_upload_fb=None,
                error_id=None,
                hidden_upload_time=None,
                a_id=None,
                b_id=None,
                c_id=None,
                alpha_id=None,
                beta_id=None,
                gamma_id=None):

    children_array = []

    if upload_id:
        _upload = dcc.Upload(id=upload_id,
                             children=html.Div([
                                 'Drag & Drop or ',
                                 html.A('Select File'),
                             ]),
                             style={
                                'width'       : '100%',
                                'height'      : '60px',
                                'lineHeight'  : '60px',
                                'borderWidth' : '1px',
                                'borderStyle' : 'dashed',
                                'borderRadius': '5px',
                                'textAlign'   : 'center',
                                'margin'      : '10px'
                             },
                             # Allow multiple files to be uploaded
                             multiple=False,
                             # last_modified=0,
                             )
        children_array.append(_upload)
        children_array.append(html.Div(id=cif_upload_fb))

    children_array.append(html.Button('Add row',
                                      id=add_row_id,
                                      n_clicks_timestamp=0))

    children_array.append(dt.DataTable(
        data=bragg_sample_df_default.to_dict('records'),
        # optional - sets the order of columns
        columns=bragg_sample_header_df.to_dict('records'),
        editable=True,
        row_selectable=False,
        filter_action='none',
        sort_action='none',
        style_cell={'textAlign': 'center'},
        row_deletable=True,
        export_format='csv',
        css=[{'selector': '.export', 'rule': 'position:absolute; left:0px; bottom:-35px'}],
        style_cell_conditional=sample_tb_even_4_col,
        style_data_conditional=[striped_rows],
        id=data_table)
    )

    children_array.append(html.Div(html.P([html.Br(), html.Br()])))

    children_array.append(dbc.Row(
            [
                dbc.Col(
                        html.Div(
                                [
                                    html.H6('a (\u212B)'),
                                    dcc.Input(id=a_id,
                                              type='number',
                                              value=3.5238,
                                              min=0.0001,
                                              inputMode='numeric',
                                              step=0.0001,
                                              ),
                                ]
                        ), width=2
                ),
                dbc.Col(
                        html.Div(
                                [
                                    html.H6('b (\u212B)'),
                                    dcc.Input(id=b_id,
                                              type='number',
                                              value=3.5238,
                                              min=0.0001,
                                              inputMode='numeric',
                                              step=0.0001,
                                              ),
                                ]
                        ), width=2
                ),
                dbc.Col(
                        html.Div(
                                [
                                    html.H6('c (\u212B)'),
                                    dcc.Input(id=c_id,
                                              type='number',
                                              value=3.5238,
                                              min=0.0001,
                                              inputMode='numeric',
                                              step=0.0001,
                                              ),
                                ]
                        ), width=2
                ),
            ]
    ))

    children_array.append(html.Div(html.P([html.Br()])))

    children_array.append(dbc.Row(
            [
                dbc.Col(
                        html.Div(
                                [
                                    html.H6('alpha (\u00b0)'),
                                    dcc.Input(id=alpha_id,
                                              type='number',
                                              value=90,
                                              min=0,
                                              inputMode='numeric',
                                              step=0.01,
                                              ),
                                ]
                        ), width=2
                ),
                dbc.Col(
                        html.Div(
                                [
                                    html.H6('beta (\u00b0)'),
                                    dcc.Input(id=beta_id,
                                              type='number',
                                              value=90,
                                              min=0,
                                              inputMode='numeric',
                                              step=0.01,
                                              ),
                                ]
                        ), width=2
                ),
                dbc.Col(
                        html.Div(
                                [
                                    html.H6('gamma (\u00b0)'),
                                    dcc.Input(id=gamma_id,
                                              type='number',
                                              value=90,
                                              min=0,
                                              inputMode='numeric',
                                              step=0.01,
                                              ),
                                ]
                        ), width=2
                ),
            ]
    ))

    # Error message div1
    children_array.append(html.Div(id=error_id, children=True))

    # Hidden div to store upload time
    children_array.append(html.Div(id=hidden_upload_time, style={'display': 'none'}))

    return children_array


# Create app layout
layout = html.Div(
    [
        dbc.Row([html.H2("Bragg Edge Simulator",
                         style=({'color': 'blue'}),
                         ),
                 ],
                class_name='title_tools',
                ),
        html.Hr(style={'borderTop': '3px solid blue'}),
        init_app_about(current_app=app_name, app_id_dict=app_id_dict),

        # Experiment input
        html.Div(
                [
                    html.H3('Global parameters:'),
                    dbc.Row(
                            [
                            dbc.Col(
                                html.Div(
                                        [
                                            html.H6('Temperature (K):'),
                                            dcc.Input(id=app_id_dict['temperature_id'],
                                                      type='number',
                                                      value=temperature_default,
                                                      min=0,
                                                      inputMode='numeric',
                                                      step=0.1,
                                                      ),
                                        ]
                                        ), width=2
                                    ),

                            dbc.Col(
                                html.Div(
                                        [
                                            html.H6('Source-to-detector (m):'),
                                            dcc.Input(id=app_id_dict['distance_id'],
                                                      type='number',
                                                      value=distance_default,
                                                      min=0,
                                                      inputMode='numeric',
                                                      step=0.01,
                                                      ),
                                        ]
                                        ), width=2
                                    ),

                            dbc.Col(
                                html.Div(
                                        [
                                            html.H6('Delay (\u03BCs):'),
                                            dcc.Input(id=app_id_dict['delay_id'],
                                                      type='number',
                                                      value=delay_default,
                                                      min=0,
                                                      inputMode='numeric',
                                                      step=0.01,
                                                      ),
                                        ]
                                        ), width=2
                                    ),
                            ]
                            ),
                ]
                ),

        html.Div(
            [
                html.H1(''),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.H6('Min. (\u212B):'),
                                    dcc.Input(id=app_id_dict['band_min_id'],
                                              type='number',
                                              inputMode='numeric',
                                              step=0.001,
                                              value=0.05,
                                              ),
                                ]
                            ), width=2
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.H6('Max. (\u212B):'),
                                    dcc.Input(id=app_id_dict['band_max_id'],
                                              type='number',
                                              inputMode='numeric',
                                              placeholder='Max.',
                                              step=0.001,
                                              value=5.5,
                                              ),
                                ]
                            ), width=2
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.H6('Step (\u212B):'),
                                    dcc.Input(id=app_id_dict['band_step_id'], type='number',
                                              inputMode='numeric',
                                              placeholder='Max.',
                                              step=0.001,
                                              value=0.005,
                                              ),
                                ]
                            ), width=2
                        ),
                    ],
                ),
            ],
        ),
        html.Hr(),
        html.H2('Input elements'),
        html.Div(),

        # tabs
        dcc.Tabs(id=app_id_dict['tabs'],
                 value='tab_user_defined',
                 children=[
                     dcc.Tab(label='User-defined',
                             value='tab_user_defined',
                             children=tab_content(add_row_id=app_id_dict['add_row_tab1'],
                                                  data_table=app_id_dict['data_table_tab1'],
                                                  error_id=app_id_dict['error_tab1'],
                                                  hidden_upload_time=app_id_dict['hidden_upload_time_tab1'],
                                                  a_id=app_id_dict['a_tab1'],
                                                  b_id=app_id_dict['b_tab1'],
                                                  c_id=app_id_dict['c_tab1'],
                                                  alpha_id=app_id_dict['alpha_tab1'],
                                                  beta_id=app_id_dict['beta_tab1'],
                                                  gamma_id=app_id_dict['gamma_tab1'],
                                                  ),
                             ),
                     dcc.Tab(label='.cif #1',
                             value='tab_cif_1',
                             children=tab_content(upload_id=app_id_dict['cif_upload_tab2'],
                                                  add_row_id=app_id_dict['add_row_tab2'],
                                                  data_table=app_id_dict['data_table_tab2'],
                                                  cif_upload_fb=app_id_dict['cif_upload_fb_tab2'],
                                                  error_id=app_id_dict['error_tab2'],
                                                  hidden_upload_time=app_id_dict['hidden_upload_time_tab2'],
                                                  a_id=app_id_dict['a_tab2'],
                                                  b_id=app_id_dict['b_tab2'],
                                                  c_id=app_id_dict['c_tab2'],
                                                  alpha_id=app_id_dict['alpha_tab2'],
                                                  beta_id=app_id_dict['beta_tab2'],
                                                  gamma_id=app_id_dict['gamma_tab2'],
                                                  )
                             ),
                     dcc.Tab(label='.cif #2',
                             value='tab_cif_2',
                             children=tab_content(upload_id=app_id_dict['cif_upload_tab3'],
                                                  add_row_id=app_id_dict['add_row_tab3'],
                                                  data_table=app_id_dict['data_table_tab3'],
                                                  cif_upload_fb=app_id_dict['cif_upload_fb_tab3'],
                                                  error_id=app_id_dict['error_tab3'],
                                                  hidden_upload_time=app_id_dict['hidden_upload_time_tab3'],
                                                  a_id=app_id_dict['a_tab3'],
                                                  b_id=app_id_dict['b_tab3'],
                                                  c_id=app_id_dict['c_tab3'],
                                                  alpha_id=app_id_dict['alpha_tab3'],
                                                  beta_id=app_id_dict['beta_tab3'],
                                                  gamma_id=app_id_dict['gamma_tab3'],
                                                  )
                             ),
                     dcc.Tab(label='.cif #3',
                             value='tab_cif_3',
                             children=tab_content(upload_id=app_id_dict['cif_upload_tab4'],
                                                  add_row_id=app_id_dict['add_row_tab4'],
                                                  data_table=app_id_dict['data_table_tab4'],
                                                  cif_upload_fb=app_id_dict['cif_upload_fb_tab4'],
                                                  error_id=app_id_dict['error_tab4'],
                                                  hidden_upload_time=app_id_dict['hidden_upload_time_tab4'],
                                                  a_id=app_id_dict['a_tab4'],
                                                  b_id=app_id_dict['b_tab4'],
                                                  c_id=app_id_dict['c_tab4'],
                                                  alpha_id=app_id_dict['alpha_tab4'],
                                                  beta_id=app_id_dict['beta_tab4'],
                                                  gamma_id=app_id_dict['gamma_tab4'],
                                                  )
                             ),
                     dcc.Tab(label='.cif #4',
                             value='tab_cif_4',
                             children=tab_content(upload_id=app_id_dict['cif_upload_tab5'],
                                                  add_row_id=app_id_dict['add_row_tab5'],
                                                  data_table=app_id_dict['data_table_tab5'],
                                                  cif_upload_fb=app_id_dict['cif_upload_fb_tab5'],
                                                  error_id=app_id_dict['error_tab5'],
                                                  hidden_upload_time=app_id_dict['hidden_upload_time_tab5'],
                                                  a_id=app_id_dict['a_tab5'],
                                                  b_id=app_id_dict['b_tab5'],
                                                  c_id=app_id_dict['c_tab5'],
                                                  alpha_id=app_id_dict['alpha_tab5'],
                                                  beta_id=app_id_dict['beta_tab5'],
                                                  gamma_id=app_id_dict['gamma_tab5'],
                                                  )
                             ),
                    ],
                ),

        # Hidden div to store df_all json
        html.Div(id=app_id_dict['hidden_df_json_id'], style={'display': 'none'}),

        # Hidden div to store df_export json
        html.Div(id=app_id_dict['hidden_df_export_json_id'], style={'display': 'none'}),

        html.Div(html.P([html.Br(), html.Br()])),

        # preview button
        html.Button('Submit',
                    style={
                           'width': '100%',
                           },
                    id=app_id_dict['submit_button_id'], n_clicks_timestamp=0),

        # Error message div1
        html.Div(id=app_id_dict['error_id'], children=True),

        html.Div(
            [
                # Plot
                bragg_plot_option_div,
                html.Div(id=app_id_dict['plot_div_id'], children=plot_loading, className='container'),
                init_display_plot_data_check(app_id_dict),

                # Data table for the plotted data
                html.Div(id=app_id_dict['df_export_tb_div']),

                # Transmission at CG-1D and stack info
                html.Div(id=app_id_dict['result_id']),
            ],
            id=app_id_dict['output_id'],
            style={'display': 'none'},
        ),
    ],
    style={'margin': '25px'}
)
