import dash_bootstrap_components as dbc

# from callbacks.bragg import *
from callbacks.bragg.main import *
from callbacks.bragg.tab1 import *
from callbacks.bragg.tab2 import *
from callbacks.bragg.tab3 import *
from callbacks.bragg.tab4 import *
from callbacks.bragg.tab5 import *
from callbacks.utilities.constants import *
from callbacks.utilities.initialization import (init_app_ids, temperature_default, distance_default, delay_default,
                                                init_app_about, init_display_plot_data_check, sample_tb_even_4_col,
                                                sample_tb_even_5_col)
from callbacks.utilities.plot import bragg_plot_option_div
from callbacks.utilities.all_apps import bragg_sample_header_df, bragg_texture_header_df

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

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    # 'padding': '6px',
    # 'fontWeight': 'bold'
}

tab_selected_style = {
    # 'borderTop': '1px solid #d6d6d6',
    # 'borderBottom': '1px solid #d6d6d6',
    # 'backgroundColor': '#119DFF',
    'backgroundColor': 'cyan',
    'color': 'black',
    # 'padding': '6px'
}

bragg_sample_df_default = pd.DataFrame({
    chem_name: [],
    index_number_h: [],
    index_number_k: [],
    index_number_l: [],
})

texture_df_default = pd.DataFrame({
    index_number_h: [],
    index_number_k: [],
    index_number_l: [],
    r: [],
    beta: [],
})


def tab_content(upload_id=None,
                add_row_id=None,
                data_table=None,
                texture_checklist_id=None,
                texture_add_row_id=None,
                texture_table=None,
                grain_size_checklist_id=None,
                grain_size_input_id=None,
                cif_upload_fb=None,
                no_error_id=None,
                hidden_upload_time=None,
                hidden_texture_add_row_time=None,
                a_id=None,
                b_id=None,
                c_id=None,
                alpha_id=None,
                beta_id=None,
                gamma_id=None,
                download_button_id=None,
                download_id=None,
                export_label_prefix=None,
                ):

    children_array = []

    if upload_id:
        _upload = dcc.Upload(id=upload_id,
                             children=html.Div([
                                 html.B('Drag'), ' & ', html.B('Drop'), ' or ', html.B('Select File'),
                                 ' (', html.I('.cif'), ' or previously ', html.I('exported structure'),
                                 ' from this page)',
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
        style_header={'fontWeight': 'bold',
                      'backgroundColor': 'lightblue'},
        row_deletable=True,
        # export_format='csv',
        css=[{'selector': '.export', 'rule': 'position:absolute; left:0px; bottom:-35px'}],
        style_cell_conditional=sample_tb_even_4_col,
        style_data_conditional=[striped_rows],
        id=data_table)
    )

    children_array.append(html.Hr())

    # Texture
    children_array.append(dcc.Checklist(
        [texture_flag],
        [],
        style={'font-size': 20},
        inline=True,
        id=texture_checklist_id,
    ))

    children_array.append(html.Button('Add row',
                                      id=texture_add_row_id,
                                      disabled=True,
                                      n_clicks_timestamp=0))

    children_array.append(dt.DataTable(
        data=texture_df_default.to_dict('records'),
        # optional - sets the order of columns
        columns=bragg_texture_header_df.to_dict('records'),
        editable=True,
        row_selectable=False,
        filter_action='none',
        sort_action='none',
        style_cell={'textAlign': 'center'},
        style_header={'fontWeight': 'bold',
                      'backgroundColor': 'lightblue'},
        row_deletable=True,
        # export_format='csv',
        css=[{'selector': '.export', 'rule': 'position:absolute; left:0px; bottom:-35px'}],
        style_cell_conditional=sample_tb_even_5_col,
        style_data_conditional=[striped_rows],
        id=texture_table,
        ),
    )

    children_array.append(html.Hr())

    # Grain size
    children_array.append(
        dbc.Row([
            dcc.Checklist(
                [grain_size_flag],
                style={'font-size': 20},
                inline=True,
                id=grain_size_checklist_id,
                ),
        ]),
    )

    children_array.append(
        dbc.Col(
            html.Div(
                [
                    dcc.Input(id=grain_size_input_id,
                              type='number',
                              value=1e-6,
                              min=1e-8,
                              inputMode='numeric',
                              disabled=True,
                              ),
                ]
            ), width=2
        ),
    )

    children_array.append(html.Hr())

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

    children_array.append(html.Div(html.P([html.Br()])))

    children_array.append(dbc.Row(html.Button('Export structure ' + export_label_prefix,
                                              id=download_button_id,
                                              n_clicks_timestamp=0)))
    children_array.append(dcc.Download(id=download_id))

    # Error message div1
    children_array.append(html.Div(id=no_error_id, children=True))

    # Hidden div to store last time we click the add row
    children_array.append(html.Div(id=hidden_upload_time, style={'display': 'none'}))

    # Hidden div to store last time we click the texture add row
    children_array.append(html.Div(id=hidden_texture_add_row_time, style={'display': 'none'}))

    col = dbc.Col(children_array,
                  style={'backgroundColor': 'cyan'})

    return col


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
                                                      step=0.001,
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
                 value='tab_cif_1',
                 colors={'background': 'white',
                         'border': 'black'},
                 children=[
                     dcc.Tab(label='Structure #1',
                             value='tab_cif_1',
                             style=tab_style,
                             selected_style=tab_selected_style,
                             children=tab_content(upload_id=app_id_dict['cif_upload_tab1'],
                                                  add_row_id=app_id_dict['add_row_tab1'],
                                                  data_table=app_id_dict['data_table_tab1'],
                                                  texture_checklist_id=app_id_dict['texture_checklist_tab1'],
                                                  texture_add_row_id=app_id_dict['texture_add_row_tab1'],
                                                  texture_table=app_id_dict['texture_table_tab1'],
                                                  grain_size_checklist_id=app_id_dict['grain_size_checklist_tab1'],
                                                  grain_size_input_id=app_id_dict['grain_size_input_tab1'],
                                                  cif_upload_fb=app_id_dict['cif_upload_fb_tab1'],
                                                  no_error_id=app_id_dict['no_error_tab1'],
                                                  hidden_upload_time=app_id_dict['hidden_upload_time_tab1'],
                                                  hidden_texture_add_row_time=app_id_dict[
                                                      'hidden_texture_add_row_time_tab1'],
                                                  a_id=app_id_dict['a_tab1'],
                                                  b_id=app_id_dict['b_tab1'],
                                                  c_id=app_id_dict['c_tab1'],
                                                  alpha_id=app_id_dict['alpha_tab1'],
                                                  beta_id=app_id_dict['beta_tab1'],
                                                  gamma_id=app_id_dict['gamma_tab1'],
                                                  download_button_id=app_id_dict['download_button_tab1'],
                                                  download_id=app_id_dict['download_tab1'],
                                                  export_label_prefix="#1",
                                                  ),
                             ),
                     dcc.Tab(label='Structure #2',
                             value='tab_cif_2',
                             style=tab_style,
                             selected_style=tab_selected_style,
                             children=tab_content(upload_id=app_id_dict['cif_upload_tab2'],
                                                  add_row_id=app_id_dict['add_row_tab2'],
                                                  data_table=app_id_dict['data_table_tab2'],
                                                  texture_checklist_id=app_id_dict['texture_checklist_tab2'],
                                                  texture_add_row_id=app_id_dict['texture_add_row_tab2'],
                                                  texture_table=app_id_dict['texture_table_tab2'],
                                                  grain_size_checklist_id=app_id_dict['grain_size_checklist_tab2'],
                                                  grain_size_input_id=app_id_dict['grain_size_input_tab2'],
                                                  cif_upload_fb=app_id_dict['cif_upload_fb_tab2'],
                                                  no_error_id=app_id_dict['no_error_tab2'],
                                                  hidden_upload_time=app_id_dict['hidden_upload_time_tab2'],
                                                  hidden_texture_add_row_time=app_id_dict[
                                                      'hidden_texture_add_row_time_tab2'],
                                                  a_id=app_id_dict['a_tab2'],
                                                  b_id=app_id_dict['b_tab2'],
                                                  c_id=app_id_dict['c_tab2'],
                                                  alpha_id=app_id_dict['alpha_tab2'],
                                                  beta_id=app_id_dict['beta_tab2'],
                                                  gamma_id=app_id_dict['gamma_tab2'],
                                                  download_id=app_id_dict['download_tab2'],
                                                  download_button_id=app_id_dict['download_button_tab2'],
                                                  export_label_prefix="#2",
                                                  )
                             ),
                     dcc.Tab(label='Structure #3',
                             value='tab_cif_3',
                             style=tab_style,
                             selected_style=tab_selected_style,
                             children=tab_content(upload_id=app_id_dict['cif_upload_tab3'],
                                                  add_row_id=app_id_dict['add_row_tab3'],
                                                  data_table=app_id_dict['data_table_tab3'],
                                                  texture_checklist_id=app_id_dict['texture_checklist_tab3'],
                                                  texture_add_row_id=app_id_dict['texture_add_row_tab3'],
                                                  texture_table=app_id_dict['texture_table_tab3'],
                                                  grain_size_checklist_id=app_id_dict['grain_size_checklist_tab3'],
                                                  grain_size_input_id=app_id_dict['grain_size_input_tab3'],
                                                  cif_upload_fb=app_id_dict['cif_upload_fb_tab3'],
                                                  no_error_id=app_id_dict['no_error_tab3'],
                                                  hidden_upload_time=app_id_dict['hidden_upload_time_tab3'],
                                                  hidden_texture_add_row_time=app_id_dict[
                                                      'hidden_texture_add_row_time_tab3'],
                                                  a_id=app_id_dict['a_tab3'],
                                                  b_id=app_id_dict['b_tab3'],
                                                  c_id=app_id_dict['c_tab3'],
                                                  alpha_id=app_id_dict['alpha_tab3'],
                                                  beta_id=app_id_dict['beta_tab3'],
                                                  gamma_id=app_id_dict['gamma_tab3'],
                                                  download_id=app_id_dict['download_tab3'],
                                                  download_button_id=app_id_dict['download_button_tab3'],
                                                  export_label_prefix="#3",
                                                  )
                             ),
                     dcc.Tab(label='Structure #4',
                             value='tab_cif_4',
                             style=tab_style,
                             selected_style=tab_selected_style,
                             children=tab_content(upload_id=app_id_dict['cif_upload_tab4'],
                                                  add_row_id=app_id_dict['add_row_tab4'],
                                                  data_table=app_id_dict['data_table_tab4'],
                                                  texture_checklist_id=app_id_dict['texture_checklist_tab4'],
                                                  texture_add_row_id=app_id_dict['texture_add_row_tab4'],
                                                  texture_table=app_id_dict['texture_table_tab4'],
                                                  grain_size_checklist_id=app_id_dict['grain_size_checklist_tab4'],
                                                  grain_size_input_id=app_id_dict['grain_size_input_tab4'],
                                                  cif_upload_fb=app_id_dict['cif_upload_fb_tab4'],
                                                  no_error_id=app_id_dict['no_error_tab4'],
                                                  hidden_upload_time=app_id_dict['hidden_upload_time_tab4'],
                                                  hidden_texture_add_row_time=app_id_dict[
                                                      'hidden_texture_add_row_time_tab4'],
                                                  a_id=app_id_dict['a_tab4'],
                                                  b_id=app_id_dict['b_tab4'],
                                                  c_id=app_id_dict['c_tab4'],
                                                  alpha_id=app_id_dict['alpha_tab4'],
                                                  beta_id=app_id_dict['beta_tab4'],
                                                  gamma_id=app_id_dict['gamma_tab4'],
                                                  download_id=app_id_dict['download_tab4'],
                                                  download_button_id=app_id_dict['download_button_tab4'],
                                                  export_label_prefix="#4",
                                                  )
                             ),
                     dcc.Tab(label='Structure #5',
                             value='tab_cif_5',
                             style=tab_style,
                             selected_style=tab_selected_style,
                             children=tab_content(upload_id=app_id_dict['cif_upload_tab5'],
                                                  add_row_id=app_id_dict['add_row_tab5'],
                                                  data_table=app_id_dict['data_table_tab5'],
                                                  texture_checklist_id=app_id_dict['texture_checklist_tab5'],
                                                  texture_add_row_id=app_id_dict['texture_add_row_tab5'],
                                                  texture_table=app_id_dict['texture_table_tab5'],
                                                  grain_size_checklist_id=app_id_dict['grain_size_checklist_tab5'],
                                                  grain_size_input_id=app_id_dict['grain_size_input_tab5'],
                                                  cif_upload_fb=app_id_dict['cif_upload_fb_tab5'],
                                                  no_error_id=app_id_dict['no_error_tab5'],
                                                  hidden_upload_time=app_id_dict['hidden_upload_time_tab5'],
                                                  hidden_texture_add_row_time=app_id_dict[
                                                      'hidden_texture_add_row_time_tab5'],
                                                  a_id=app_id_dict['a_tab5'],
                                                  b_id=app_id_dict['b_tab5'],
                                                  c_id=app_id_dict['c_tab5'],
                                                  alpha_id=app_id_dict['alpha_tab5'],
                                                  beta_id=app_id_dict['beta_tab5'],
                                                  gamma_id=app_id_dict['gamma_tab5'],
                                                  download_id=app_id_dict['download_tab5'],
                                                  download_button_id=app_id_dict['download_button_tab5'],
                                                  export_label_prefix="#5",
                                                  )
                             ),
                 ],
            ),

        html.Hr(),

        # Hidden div to store df_all json
        html.Div(id=app_id_dict['hidden_df_json_id'], style={'display': 'none'}),

        # Hidden div to store df_all json
        html.Div(id=app_id_dict['no_error_id'], style={'display': 'none'}),

        # Hidden div to store df_export json
        html.Div(id=app_id_dict['hidden_df_export_json_id'], style={'display': 'none'}),

        html.Div(html.P([html.Br(), html.Br()])),

        # preview button
        html.Button('Submit',
                    style={
                        'width': '100%',
                    },
                    id=app_id_dict['submit_button_id'], n_clicks_timestamp=0),

        dcc.Loading(id='loading',
                    type='circle',
                    children=[html.Div([html.Div(id="loading-output-2",
                                                 style={'display': 'none'},
                                                 ),
                                        ])],
                    ),

        # Error message div1
        html.Div(id=app_id_dict['general_processing_errors']),

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
