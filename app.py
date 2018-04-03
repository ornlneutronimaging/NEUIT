import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output

from _app import app, server
from apps import app1, app2

app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
        # The above line is a get-around this issue by rendering a hidden dash-table-experiments component in the layout
        html.Div(id='page-content'),
    ], className='ten columns offset-by-one'
)

index_page = html.Div(
    [
        # Heading section
        html.Div(
            [
                html.H1('NeuWeb'),
            ], className="row"
        ),
        dcc.Markdown('''
Web applications for **Neutron Imaging**.
'''),
        html.H6('Tools available are:'),
        dcc.Link('1. Cold neutron transmission', href='/apps/cg1d'),
        html.Br(),
        dcc.Link('2. Neutron resonance', href='/apps/venus'),
        dcc.Markdown('''
#### Introduction

Tools available here are build upon *[ImagingReso](http://imagingreso.readthedocs.io/en/latest/)*
using *[Dash](https://dash.plot.ly/)* framework. 

*ImagingReso* is an open-source Python library that simulates the neutron
resonance signal for neutron imaging measurements. By defining the sample
information such as density, thickness in the neutron path, and isotopic
ratios of the elemental composition of the material, this package plots
the expected resonance peaks for a selected neutron energy range.

The energy dependent cross-section data used are from
[National Nuclear Data Center](http://www.nndc.bnl.gov/), a published
online database. [Evaluated Nuclear Data File](http://www.nndc.bnl.gov/exfor/endf00.jsp)
([ENDF/B-VII.1](https://www.sciencedirect.com/science/article/pii/S009037521100113X)) 
is currently supported and more evaluated databases will be added in the future.
'''),
        dcc.Markdown('''
#### Publication

Yuxuan Zhang and Jean Bilheux, (2017), ImagingReso: A Tool for Neutron Resonance Imaging, Journal of Open Source Software, 2(19), 407,
[doi:10.21105/joss.00407](http://joss.theoj.org/papers/997d09281a9d76e95f4ec4d3279eeb8c)
'''),
    ]
)


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname is None:
        return 'loading...'
    elif pathname == '/apps/cg1d':
        return app1.layout
    elif pathname == '/apps/venus':
        return app2.layout
    elif pathname == '/':
        return index_page
    else:
        return '404: URL not found'


if __name__ == '__main__':
    app.run_server(debug=True)
