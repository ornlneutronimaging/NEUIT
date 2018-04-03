import os

import dash

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
server = app.server
server.secret_key = os.environ.get('secret_key', 'secret')

external_css = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
]
for css in external_css:
    app.css.append_css({"external_url": css})

