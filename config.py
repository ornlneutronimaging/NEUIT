import dash
import os
import dash_bootstrap_components as dbc
from dash import dcc


app_dict = {'transmission' : {'name': 'Neutron transmission',
                              'url' : '/transmission'},
            'resonance'    : {'name': 'Neutron resonance',
                              'url' : '/resonance'},
            'converter'    : {'name': 'Composition converter',
                              'url' : '/converter'},
            'tof_plotter'  : {'name': 'Time-of-flight plotter (under testing)',
                              'url' : '/tof_plotter'},
            'bragg'        : {'name': 'Bragg-edge simulator (under testing)',
                              'url' : '/bragg'},
            'golden_angles': {'name': 'Golden Angles',
                              'url' : '/golden_angles'}
            }

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [dbc.themes.COSMO,
                        'https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
server.secret_key = os.environ.get('secret_key', 'secret')
app.config.suppress_callback_exceptions = True
app.title = 'iNEUIT'

app_info_markdown_dict = {
    'transmission': dcc.Markdown("""
    This tool estimates the neutron transmission/attenuation signals and contrast,
    by defining the sample information such as density, thickness in the neutron beam path.
    Multiple samples or complex compounds can be added as layers in such calculation. 
    Estimating the contrast by changing isotopic ratios is also supported.
    An example is shown by default to demonstrate its usage.
            """),
    'resonance': dcc.Markdown("""
    This tool estimates the energy dependent neutron imaging signals and contrasts,
    specifically for *resonances* in the *epithermal* range.
    Similar to the transmission tool, sample/samples can be entered as layers in such calculation. 
    Estimating the contrast by changing isotopic ratios is also supported.
    An example is shown by default to demonstrate its usage.
            """),
    'converter': dcc.Markdown("""
    This tool helps the conversion between wt.% and at.%. And it populates
    an equivalent chemical formula to represent a complex mixture. Such formula
    can be used as '{}' in other tools available in NEUIT.
    An example is shown by default to demonstrate its usage.
            """.format("Chemical formula")),
    'tof_plotter': dcc.Markdown("""
    This tool helps plotting data acquired from Timepix2 MCP detector. By dragging and dropping
    spectra files and data files, one can quickly verify if expected resonances or Bragg-edges
    have been captured or not. Optional background file can also be added if normalization is needed.  
            """),
    'bragg': dcc.Markdown("""
    This tool estimates the energy dependent neutron imaging signals and contrasts,
    specifically for *Bragg-edges* in the *cold* or *thermal* range. Currently, it only supports
    dragging and dropping '.cif' files.
            """),
}
