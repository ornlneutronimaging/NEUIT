import dash
import os
import dash_bootstrap_components as dbc

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
