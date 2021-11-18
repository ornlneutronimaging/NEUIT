import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import matplotlib as mpl

mpl.use('agg')  # this is to fix the matplotlib backend

from _utilities import app_links_div, app_dict
from _app import app
from apps import app1, app2, app3, app4, app5, app6

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
        dcc.Markdown('''**NEU**tron **I**maging **T**oolbox (v0.0.22)'''),
        html.H6('Available tools:'),
        app_links_div,
        dcc.Markdown('''
#### Introduction

Here we present a toolbox to provide interactive and user-friendly applications
that can be used for Neutron Imaging related calculations.

Tools available here are build upon open source libraries, such as 
*[ImagingReso](https://imagingreso.readthedocs.io/en/latest/)*,
*[periodictable](https://periodictable.readthedocs.io/en/latest/)*,
*[braggedgemodeling](https://ornlneutronimaging.github.io/braggedgemodeling/)*, etc.,
using *[Dash](https://dash.plot.ly/)* framework. 

Detailed functionality description is available inside each application.

'''),

        dcc.Markdown('''
#### Disclaimer

The energy dependent cross-section data used are from
[National Nuclear Data Center](http://www.nndc.bnl.gov/), a published
online database. [Evaluated Nuclear Data File](http://www.nndc.bnl.gov/exfor/endf00.jsp),
[ENDF/B-VIII.0](https://www.sciencedirect.com/science/article/pii/S0090375218300206) and 
[ENDF/B-VII.1](https://www.sciencedirect.com/science/article/pii/S009037521100113X)
are currently supported. More evaluated database will be added in the future.

Please note that the energy dependent cross-section of hydrogen in ENDF/B database
is for a free H atom. When interacting with slow neutrons in the cold range, the
cross-section of a bonded H could be underestimated when using this tool. 
In a recent update to support *[ImagingReso (v1.7.4)](https://github.com/ornlneutronimaging/ImagingReso/releases/tag/v1.7.4)*,
some experimentally measured cross-sections ([ref1](https://journals.aps.org/pr/abstract/10.1103/PhysRev.76.1750) and
[ref2](https://t2.lanl.gov/nis/data/endf/endfvii-thermal.html)) of a bonded H are now available.
'''),
        dcc.Markdown('''
#### Cite this work

1.Yuxuan Zhang, Jean Bilheux, Hassina Bilheux and Jiao Lin, (2019) "[An interactive web-based tool 
to guide the preparation of neutron imaging experiments at oak ridge national laboratory](https://iopscience.iop.org/article/10.1088/2399-6528/ab4ee6)", 
*Journal of Physics Communications*, 3(10), 103003.

2.Yuxuan Zhang and Jean Bilheux, (2017), "[ImagingReso: A Tool for Neutron Resonance Imaging](http://joss.theoj.org/papers/997d09281a9d76e95f4ec4d3279eeb8c)",
*Journal of Open Source Software*, 2(19), 407.

'''),
        dcc.Markdown('''
#### Contact us

Yuxuan Zhang -- zhangy6@ornl.gov

Jean Bilheux -- bilheuxjm@ornl.gov
'''),

        dcc.Markdown('''
#### Acknowledgments

This work is based upon research sponsored by the Laboratory Directed Research and
Development Program of Oak Ridge National Laboratory, managed by UT-Battelle LLC for
the US Department of Energy. This research used resources at the Spallation Neutron Source,
a DOE Office of Science User Facility operated by Oak Ridge National Laboratory.
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
    elif pathname == app_dict['app4']['url']:
        return app4.layout
    elif pathname == app_dict['app5']['url']:
        return app5.layout
    elif pathname == app_dict['app6']['url']:
        return app6.layout
    elif pathname == '/':
        return index_page
    else:
        return '404: URL not found'


if __name__ == '__main__':
    app.run_server(debug=False)
