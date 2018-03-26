import ImagingReso._utilities as ir_util
import pandas as pd
from ImagingReso.resonance import Resonance


def init_reso(e_min, e_max, e_step):
    o_reso = Resonance(energy_min=e_min, energy_max=e_max, energy_step=e_step)
    return o_reso


def load_beam_shape(relative_path_to_beam_shape):
    # _path_to_beam_shape = 'static/instrument_file/beam_shape_cg1d.txt'
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


def unpack_tb_df_and_add_layer(o_reso, sample_tb_df):
    num_layer = len(sample_tb_df['Chemical formula'])
    for i in range(num_layer):
        if sample_tb_df['Chemical formula'][i] != '' and sample_tb_df['Thickness (mm)'][i] != '':
            if sample_tb_df['Density (g/cm^3)'][i] == '':
                o_reso.add_layer(formula=sample_tb_df['Chemical formula'][i],
                                 thickness=float(sample_tb_df['Thickness (mm)'][i]))
            else:
                o_reso.add_layer(formula=sample_tb_df['Chemical formula'][i],
                                 density=float(sample_tb_df['Density (g/cm^3)'][i]),
                                 thickness=float(sample_tb_df['Thickness (mm)'][i]))
    return o_reso
