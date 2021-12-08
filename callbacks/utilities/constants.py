from dash import html
from dash import dcc


energy_name = 'Energy (eV)'
wave_name = 'Wavelength (\u212B)'
speed_name = 'Speed (m/s)'
tof_name = 'Time-of-flight (\u03BCs)'
number_name = 'Image index (#)'
class_name = 'Neutron classification'
chem_name = 'Chemical formula'
thick_name = 'Thickness (mm)'
density_name = 'Density (g/cm\u00B3)'
ratio_name = 'Stoichiometric ratio'
molar_name = 'Molar mass (g/mol)'
number_density_name = 'Atoms (#/cm\u00B3)'
mu_per_cm_name = 'Attenu. co. (/cm)'
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

label_sample = html.Label(['When omitted, natural densities will be used. List of densities can be found ',
                           html.A("here.", href='http://periodictable.com/Properties/A/Density.al.html',
                                  target="_blank")])

markdown_compos = dcc.Markdown('''
NOTE: *formula* is **CASE SENSITIVE**, *stoichiometric ratio* must be an **INTEGER**.''')

markdown_iso = dcc.Markdown('''
NOTE: Uncheck the box will **NOT RESET** this table if you have edited it, but the input will not be used in the
calculations.''')