import dash
import dash_bootstrap_components as dbc
import os

external_stylesheets = [dbc.themes.JOURNAL, "assets/style.css"]
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
#                 meta_tags=[{'name': 'viewport',
#                             'content': 'width=device-width, '
#                                        'initial-scale=1.0, '
#                                        'maximum-scale=4, '
#                                        'minimum-scale=0.5'}])
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                meta_tags=[{'name': 'viewport',
                            }])
app.config.suppress_callback_exceptions = True

server = app.server
server.secret_key = os.environ.get('secret_key', 'secret')
app.title = 'iNEUIT'
