from dash import html
from dash import dcc

peak_wave = {'mars': 2.53,  # AA
             'mars_crop': 2.52,  # Don't change to 2.53
             'snap': 1.8,
             'venus': 1.8,
             }
index_number_a = 'a'
index_number_b = 'b'
index_number_c = 'c'
index_number_h = 'h'
index_number_k = 'k'
index_number_l = 'l'
axial_length_a = 'a (\u212B)'
axial_length_b = 'b (\u212B)'
axial_length_c = 'c (\u212B)'
r = 'r'
beta = 'beta (rad)'
texture_flag = 'Texture'
grain_size_flag = ' Grain size (mm)'
interaxial_angle_alpha = 'alpha (\u00b0)'
interaxial_angle_beta = 'beta (\u00b0)'
interaxial_angle_gamma = 'gamma (\u00b0)'
energy_name = 'Energy (eV)'
wave_name = 'Wavelength (\u212B)'
speed_name = 'Speed (m/s)'
tof_name = 'Time-of-flight (\u03BCs)'
number_name = 'Image index (#)'
class_name = 'Neutron classification'
chem_name = 'Chemical formula'
atom = "Atom"
thick_name = 'Thickness (mm)'
density_name = 'Density (g/cm\u00B3)'
ratio_name = 'Stoichiometric ratio'
molar_name = 'Molar mass (g/mol)'
number_density_name = 'Atoms (#/cm\u00B3)'
mu_per_cm_name = 'Attenu. co. (/cm)'
mu_per_cm_at_peak_name = u'Attenu. co. at 2.53 \u212B(/cm)'
# mu_per_cm_at_peak_name = u'Attenu. co. at peak wavelength(/cm)'
# mu_per_cm_at_peak_name = u'Attenu. co. at peak (or close to peak) wavelength(/cm)'
layer_name = 'Layer'
ele_name = 'Element'
iso_name = 'Isotope'
iso_ratio_name = 'Isotopic ratio'
weight_name = 'Weight (g)'
weight_name_p = 'Weight %'
atomic_name = 'Atoms (mol)'
atomic_name_p = 'Atomic %'
compos_2nd_col_id = '2nd_input_column'


col_width_1 = 'one column'
col_width_3 = 'three columns'
col_width_5 = 'five columns'
col_width_6 = 'six columns'
empty_div = html.Div()


markdown_sample = dcc.Markdown('''
NOTE: *formula* is **CASE SENSITIVE**, *stoichiometric ratio* must be an **INTEGER**. Density input can **ONLY**
be **omitted (leave as blank)** if the input formula is a single element.''')

markdown_disclaimer_sns = dcc.Markdown('''
**Disclaimer**: estimations are solely based on the energy/wavelength dependent total cross-sections 
from **ENDF/B** database and the **simulated** beam spectrum at this beamline.''')

markdown_disclaimer_hfir = dcc.Markdown('''
**Disclaimer**: estimations are solely based on the energy/wavelength dependent total cross-sections 
from **ENDF/B** database and the **measured** beam spectrum at this beamline.''')

markdown_disclaimer_hydrogen = dcc.Markdown('''
**Note**: inelastic scattering for **lighter isotopes (H, D)** is both temperature and material dependent and will 
not be included in the calculations. In particular, **attenuation** and **attenuation coefficient** are going to be
significantly **underestimated**.  \n Attenuation of 5 mm thick H2O is estimated to be 76.2 %, but the
measured attenuation at MARS is ~90 %.  \n Attenuation of 5 mm thick D2O is estimated to be 20.6 %, but the 
measured attenuation at MARS is ~30 %.''')

label_sample = html.Label(['When omitted, natural densities will be used. List of densities can be found ',
                           html.A("here.", href='http://periodictable.com/Properties/A/Density.al.html',
                                  target="_blank")])

markdown_compos = dcc.Markdown('''
NOTE: *formula* is **CASE SENSITIVE**, *stoichiometric ratio* must be an **INTEGER**.''')

markdown_iso = dcc.Markdown('''
NOTE: Uncheck the box will **NOT RESET** this table if you have edited it, but the input will not be used in the
calculations.''')
