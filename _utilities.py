import os

import ImagingReso._utilities as ir_util
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
from ImagingReso.resonance import Resonance
from scipy.interpolate import interp1d

energy_name = 'Energy (eV)'
wave_name = 'Wavelength (\u212B)'
speed_name = 'Speed (m/s)'
tof_name = 'Time-of-flight (\u03BCs)'
class_name = 'Neutron classification'
range_tb_header = [energy_name, wave_name, speed_name, tof_name, class_name]

chem_name = 'Chemical formula'
thick_name = 'Thickness (mm)'
density_name = 'Density (g/cm\u00B3)'
sample_tb_header = [chem_name, thick_name, density_name]

layer_name = 'Layer'
ele_name = 'Element'
iso_name = 'Isotope'
iso_ratio_name = 'Isotopic ratio'
iso_table_header = [layer_name, ele_name, iso_name, iso_ratio_name]
iso_tb_rows_default = [{ele_name: None, iso_name: None, iso_ratio_name: None, layer_name: None}]
iso_tb_df_default = pd.DataFrame(iso_tb_rows_default)
col_3 = 'three columns'
col_6 = 'six columns'


def classify_neutron(energy_ev):
    """

    :param energy_ev:
    :return:
    """
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


def init_reso_from_tb(range_tb_rows, e_step):
    df_range_tb = pd.DataFrame(range_tb_rows)
    e_min = df_range_tb[energy_name][0]
    e_max = df_range_tb[energy_name][1]
    o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
    return o_reso


def load_beam_shape(relative_path_to_beam_shape):
    # Load beam shape from static
    df = pd.read_csv(relative_path_to_beam_shape, sep='\t', skiprows=0)
    df.columns = ['wavelength_A', 'flux']
    # Get rid of crazy data
    df.drop(df[df.wavelength_A < 0].index, inplace=True)
    df.drop(df[df.flux <= 0].index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # Convert wavelength to energy
    energy_list = ir_util.angstroms_to_ev(df['wavelength_A'])
    df.insert(1, 'energy_eV', energy_list)
    return df


def unpack_sample_tb_df_and_add_layer(o_reso, sample_tb_df):
    num_layer = len(sample_tb_df['Chemical formula'])
    for i in range(num_layer):
        if sample_tb_df[chem_name][i] != '' and sample_tb_df[thick_name][i] != '':
            if sample_tb_df[density_name][i] == '':
                o_reso.add_layer(formula=sample_tb_df[chem_name][i],
                                 thickness=float(sample_tb_df[thick_name][i]))
            else:
                o_reso.add_layer(formula=sample_tb_df[chem_name][i],
                                 density=float(sample_tb_df[density_name][i]),
                                 thickness=float(sample_tb_df[thick_name][i]))
    return o_reso


def unpack_iso_tb_df_and_update(o_reso, iso_tb_df, iso_changed):
    # if layer_name not in iso_tb_df.columns:
    if len(iso_changed) == 0:
        return o_reso
    else:
        layer_list = list(o_reso.stack.keys())
        for each_layer in layer_list:
            element_list = o_reso.stack[each_layer]['elements']
            for each_ele in element_list:
                _ele_ratio_list = []
                for i in range(len(iso_tb_df)):
                    if each_layer == iso_tb_df[layer_name][i] and each_ele == iso_tb_df[ele_name][i]:
                        _ele_ratio_list.append(float(iso_tb_df[iso_ratio_name][i]))
                o_reso.set_isotopic_ratio(compound=each_layer, element=each_ele, list_ratio=_ele_ratio_list)
        return o_reso


def add_del_tb_rows(n_add, n_del, sample_tb_rows):
    if n_add is None:
        n_add = 0
    if n_del is None:
        n_del = 0
    df_sample_tb = pd.DataFrame(sample_tb_rows)
    if chem_name not in df_sample_tb.columns:
        df_sample_tb[chem_name] = ['']
    if thick_name not in df_sample_tb.columns:
        df_sample_tb[thick_name] = ['']
    if density_name not in df_sample_tb.columns:
        df_sample_tb[density_name] = ['']
    n_layer = len(df_sample_tb[chem_name])
    _formula_list = list(df_sample_tb[chem_name])
    _thickness_list = list(df_sample_tb[thick_name])
    _density_list = list(df_sample_tb[density_name])
    n_row = n_add - n_del + 1
    if n_row > n_layer:
        _formula_list.append('')
        _thickness_list.append('')
        _density_list.append('')
    elif n_row < n_layer:
        _formula_list.pop()
        _thickness_list.pop()
        _density_list.pop()
    _df_sample = pd.DataFrame({
        chem_name: _formula_list,
        thick_name: _thickness_list,
        density_name: _density_list,
    })
    return _df_sample


def calculate_transmission_cg1d_and_form_stack_table(sample_tb_rows, iso_tb_rows, iso_changed):
    _main_path = os.path.abspath(os.path.dirname(__file__))
    _path_to_beam_shape = os.path.join(_main_path, 'static/instrument_file/beam_shape_cg1d.txt')
    df = load_beam_shape(_path_to_beam_shape)
    __o_reso = Resonance(energy_min=0.00025, energy_max=0.12525, energy_step=0.000625)

    df_sample_tb = pd.DataFrame(sample_tb_rows)
    _o_reso = unpack_sample_tb_df_and_add_layer(o_reso=__o_reso, sample_tb_df=df_sample_tb)
    df_iso_tb = pd.DataFrame(iso_tb_rows)
    o_reso = unpack_iso_tb_df_and_update(o_reso=_o_reso, iso_tb_df=df_iso_tb, iso_changed=iso_changed)

    # interpolate with the beam shape energy
    interp_type = 'cubic'
    energy = o_reso.total_signal['energy_eV']
    trans = o_reso.total_signal['transmission']
    interp_function = interp1d(x=energy, y=trans, kind=interp_type)
    # add interpolated transmission value to beam shape df
    trans = interp_function(df['energy_eV'])
    # calculated transmitted flux
    trans_flux = trans * df['flux']
    _total_trans = sum(trans_flux) / sum(df['flux']) * 100
    # total_trans = round(_total_trans, 3)

    o_stack = o_reso.stack
    div_list = []
    layers = list(o_stack.keys())
    layer_dict = {}
    for l, layer in enumerate(layers):
        elements_in_current_layer = o_stack[layer]['elements']
        l_str = str(l + 1)
        current_layer_list = [
            html.P("Layer {}: {}".format(l_str, layer)),
        ]
        layer_dict[thick_name] = o_stack[layer]['thickness']['value']
        layer_dict[density_name] = round(o_stack[layer]['density']['value'], 4)
        _df_layer = pd.DataFrame([layer_dict])
        current_layer_list.append(
            dt.DataTable(rows=_df_layer.to_dict('records'),
                         columns=[thick_name, density_name],
                         editable=False,
                         row_selectable=False,
                         filterable=False,
                         sortable=False,
                         # id='sample_table'
                         ))

        for e, ele in enumerate(elements_in_current_layer):
            _iso_list = o_stack[layer][ele]['isotopes']['list']
            _iso_ratios = o_stack[layer][ele]['isotopes']['isotopic_ratio']
            iso_dict = {}
            for i, iso in enumerate(_iso_list):
                iso_dict[iso] = round(_iso_ratios[i], 4)
            _df_iso = pd.DataFrame([iso_dict])
            current_layer_list.append(
                dt.DataTable(rows=_df_iso.to_dict('records'),
                             columns=_df_iso.columns,
                             editable=False,
                             row_selectable=False,
                             filterable=False,
                             sortable=False,
                             ))

        div_list.append(html.Div(current_layer_list))
        div_list.append(html.Br())

    return _total_trans, div_list


def form_iso_table(sample_tb_rows):
    o_reso = Resonance(energy_min=1, energy_max=2, energy_step=1)
    df_sample_tb = pd.DataFrame(sample_tb_rows)
    o_reso = unpack_sample_tb_df_and_add_layer(o_reso=o_reso, sample_tb_df=df_sample_tb)
    layer_list = list(o_reso.stack.keys())
    lay_list = []
    ele_list = []
    iso_list = []
    iso_ratio_list = []
    for each_layer in layer_list:
        current_ele_list = o_reso.stack[each_layer]['elements']
        for each_ele in current_ele_list:
            current_iso_list = o_reso.stack[each_layer][each_ele]['isotopes']['list']
            current_iso_ratio_list = o_reso.stack[each_layer][each_ele]['isotopes']['isotopic_ratio']
            for i, each_iso in enumerate(current_iso_list):
                lay_list.append(each_layer)
                ele_list.append(each_ele)
                iso_list.append(each_iso)
                iso_ratio_list.append(round(current_iso_ratio_list[i], 4))

    _dict = {'Layer': lay_list,
             'Element': ele_list,
             'Isotope': iso_list,
             'Isotopic ratio': iso_ratio_list,
             }
    _df = pd.DataFrame(_dict)

    return _df


# Plot control buttons
plot_option_div = html.Div(
    [
        html.Hr(),
        html.H3('Result'),
        html.H5('Plot:'),
        html.Div(
            [
                html.Div(
                    [
                        html.P('X options: '),
                        dcc.RadioItems(id='x_type',
                                       options=[
                                           {'label': 'Energy (eV)', 'value': 'energy'},
                                           {'label': 'Wavelength (\u212B)', 'value': 'lambda'},
                                           {'label': 'Time-of-flight (\u03BCs)', 'value': 'time'},
                                       ],
                                       value='energy',
                                       )
                    ], className=col_3
                ),
                html.Div(
                    [
                        html.P('Y options: '),
                        dcc.RadioItems(id='y_type',
                                       options=[
                                           {'label': 'Attenuation', 'value': 'attenuation'},
                                           {'label': 'Transmission', 'value': 'transmission'},
                                           {'label': 'Total cross-section (barn)', 'value': 'sigma'}
                                       ],
                                       value='attenuation',
                                       )
                    ], className=col_3
                ),
                html.Div(
                    [
                        html.P('Scale options: '),
                        dcc.RadioItems(id='plot_scale',
                                       options=[
                                           {'label': 'Linear', 'value': 'linear'},
                                           {'label': 'Log x', 'value': 'logx'},
                                       ],
                                       value='linear',
                                       )
                    ], className=col_3
                ),
                html.Div(
                    [
                        html.P('Show options: '),
                        dcc.Checklist(id='show_opt',
                                      options=[
                                          {'label': 'Total', 'value': 'total'},
                                          {'label': 'Layer', 'value': 'layer'},
                                          {'label': 'Element', 'value': 'ele'},
                                          {'label': 'Isotope', 'value': 'iso'},
                                      ], values=['iso'],
                                      ),
                    ], className=col_3
                ),
            ], className='row'
        ),
    ]
),
