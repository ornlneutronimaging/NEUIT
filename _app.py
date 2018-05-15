import dash
import os

app = dash.Dash()
server = app.server
server.secret_key = os.environ.get('secret_key', 'secret')
app.config.suppress_callback_exceptions = True
app.title = 'ONIST'

external_css = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
]
for css in external_css:
    app.css.append_css({"external_url": css})

