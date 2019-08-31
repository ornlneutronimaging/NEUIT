import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import matplotlib as mpl

mpl.use('agg')  # this is to fix the matplotlib backend

from _utilities import app_links_div, app_dict
from _app import app
from apps import app1, app2, app3

server = app.server

app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content'),
    ], className='ten columns offset-by-one'
)

app_name = 'home'

index_page = html.Div(
    [
        # Heading section
        html.Div(
            [
                html.H1('NEUIT'),
            ], className="row"
        ),
        dcc.Markdown('''**NEU**tron **I**maging **T**oolbox'''),
        html.H6('Tools available are:'),
        app_links_div,
        dcc.Markdown('''
#### Introduction

Tools available here are build upon *[ImagingReso](https://imagingreso.readthedocs.io/en/latest/)*
using *[Dash](https://dash.plot.ly/)* framework. 

*ImagingReso* is an open-source Python library that simulates the neutron
resonance signal for neutron imaging measurements. By defining the sample
information such as density, thickness in the neutron path, and isotopic
ratios of the elemental composition of the material, this package plots
the expected resonance peaks for a selected neutron energy range.

The energy dependent cross-section data used are from
[National Nuclear Data Center](http://www.nndc.bnl.gov/), a published
online database. [Evaluated Nuclear Data File](http://www.nndc.bnl.gov/exfor/endf00.jsp)
([ENDF/B-VIII.0](https://www.sciencedirect.com/science/article/pii/S0090375218300206)) 
is currently supported and more evaluated databases will be added in the future.

*[PeriodicTable](https://periodictable.readthedocs.io/en/latest/)* provides various 
elements/isotopes related properties in the calculations.
'''),
        # [ENDF/B-VII.1](https://www.sciencedirect.com/science/article/pii/S009037521100113X)
        dcc.Markdown('''
#### Acknowledgments

This work is based upon research sponsored by the Laboratory Directed Research and
Development Program of Oak Ridge National Laboratory, managed by UT-Battelle LLC for
the US Department of Energy. This research used resources at the Spallation Neutron Source,
a DOE Office of Science User Facility operated by Oak Ridge National Laboratory.
'''),
        dcc.Markdown('''
#### Cite our work

Yuxuan Zhang and Jean Bilheux, (2017), ImagingReso: A Tool for Neutron Resonance Imaging,
Journal of Open Source Software, 2(19), 407,
[doi:10.21105/joss.00407](http://joss.theoj.org/papers/997d09281a9d76e95f4ec4d3279eeb8c)
'''),
        dcc.Markdown('''
#### Contact

Yuxuan Zhang -- zhangy6@ornl.gov

Jean Bilheux -- bilheuxjm@ornl.gov
'''),
    ]
)


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname is None:
        return 'loading...'
    elif pathname == app_dict['app1']['url']:
        return app1.layout
    elif pathname == app_dict['app2']['url']:
        return app2.layout
    elif pathname == app_dict['app3']['url']:
        return app3.layout
    elif pathname == '/':
        return index_page
    else:
        return '404: URL not found'


if __name__ == '__main__':
    app.run_server(debug=True)
