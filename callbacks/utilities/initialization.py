def init_app_ids(app_name: str):
    id_dict = {}
    id_dict['more_about_app_id'] = app_name + '_more_about_app'
    id_dict['app_info_id'] = app_name + '_app_info'
    id_dict['sample_upload_id'] = app_name + '_sample_upload'
    id_dict['error_upload_id'] = app_name + '_error_upload'
    id_dict['hidden_upload_time_id'] = app_name + '_time_upload'
    id_dict['add_row_id'] = app_name + '_add_row'
    id_dict['del_row_id'] = app_name + '_del_row'
    id_dict['database_id'] = app_name + '_database'
    id_dict['sample_table_id'] = app_name + '_sample_table'
    id_dict['iso_check_id'] = app_name + '_iso_check'
    id_dict['iso_div_id'] = app_name + '_iso_input'
    id_dict['iso_table_id'] = app_name + '_iso_table'
    id_dict['submit_button_id'] = app_name + '_submit'
    id_dict['result_id'] = app_name + '_result'
    id_dict['error_id'] = app_name + '_error'
    id_dict['output_id'] = app_name + '_output'

    if app_name == 'transmission':  # id names for neutron transmission only
        id_dict['beamline_id'] = app_name + '_beamline'
        id_dict['band_div_id'] = app_name + '_band_div'
        id_dict['band_min_id'] = app_name + '_band_min'
        id_dict['band_max_id'] = app_name + '_band_max'
        id_dict['band_type_id'] = app_name + '_band_type'
        id_dict['band_unit_id'] = app_name + '_band_unit'

    elif app_name == 'resonance':  # id names for neutron resonance only
        id_dict['slider_id'] = app_name + '_e_range_slider'
        id_dict['range_table_id'] = app_name + '_range_table'
        id_dict['e_step_id'] = app_name + '_e_step'
        id_dict['distance_id'] = app_name + '_distance'
        id_dict['hidden_prev_distance_id'] = app_name + '_hidden_prev_distance'
        id_dict['hidden_range_input_coord_id'] = app_name + '_hidden_range_input_coord'
        id_dict['hidden_df_export_json_id'] = app_name + '_hidden_df_export_json'
        id_dict['hidden_df_json_id'] = app_name + '_hidden_df_json'
        id_dict['df_export_tb_div'] = app_name + '_df_export_tb_div'
        id_dict['df_export_tb'] = app_name + '_df_export_tb'
        id_dict['plot_div_id'] = app_name + '_plot'
        id_dict['plot_fig_id'] = app_name + '_plot_fig'
        id_dict['plot_options_div_id'] = app_name + '_plot_options'
        id_dict['display_plot_data_id'] = app_name + '_display_plot_data'
        id_dict['prev_x_type_id'] = app_name + '_prev_x_type'

    elif app_name == 'converter':  # id names for composition converter only
        id_dict['compos_type_id'] = app_name + '_compos_input_type'

    elif app_name == 'tof_plotter':  # id names for TOF plotter only
        id_dict['distance_id'] = app_name + '_distance'
        id_dict['delay_id'] = app_name + '_delay'
        id_dict['spectra_upload_id'] = app_name + '_spectra'
        id_dict['spectra_upload_fb_id'] = app_name + '_spectra_fb'
        id_dict['data_upload_id'] = app_name + '_data'
        id_dict['data_upload_fb_id'] = app_name + '_data_fb'
        id_dict['background_upload_id'] = app_name + '_background'
        id_dict['background_check_id'] = app_name + '_background_ck'
        id_dict['background_upload_fb_id'] = app_name + '_background_fb'
        id_dict['plot_div_id'] = app_name + '_plot'
        id_dict['plot_fig_id'] = app_name + '_plot_fig'

    elif app_name == 'bragg':  # id names for bragg edge simulator only
        id_dict['error_id2'] = app_name + '_error2'
        id_dict['temperature_id'] = app_name + '_temperature'
        id_dict['distance_id'] = app_name + '_distance'
        id_dict['band_min_id'] = app_name + '_band_min'
        id_dict['band_max_id'] = app_name + '_band_max'
        id_dict['band_step_id'] = app_name + '_band_step'
        id_dict['band_unit_id'] = app_name + '_band_unit'
        id_dict['cif_upload_id'] = app_name + '_cif'
        id_dict['cif_upload_fb_id'] = app_name + '_cif_fb'
        id_dict['hidden_df_json_id'] = app_name + '_hidden_df_json'
        id_dict['hidden_df_export_json_id'] = app_name + '_hidden_df_export_json'
        id_dict['df_export_tb_div'] = app_name + '_df_export_tb_div'
        id_dict['df_export_tb'] = app_name + '_df_export_tb'
        id_dict['plot_div_id'] = app_name + '_plot'
        id_dict['plot_fig_id'] = app_name + '_plot_fig'
        id_dict['display_plot_data_id'] = app_name + '_display_plot_data'

    return id_dict