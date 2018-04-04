import dash

app = dash.Dash()
server = app.server
app.config.supress_callback_exceptions = True
app.title = 'NeuWeb'

external_css = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
]
for css in external_css:
    app.css.append_css({"external_url": css})

