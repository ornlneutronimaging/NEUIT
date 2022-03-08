import plotly.tools as tls
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc


def shape_matplot_to_plotly(fig, y_type, plot_scale):
    plotly_fig = tls.mpl_to_plotly(fig)
    # Layout
    plotly_fig.layout.showlegend = True
    plotly_fig.layout.autosize = True
    plotly_fig.layout.height = 600
    plotly_fig.layout.width = 900
    plotly_fig.layout.margin = {'b': 52, 'l': 80, 'pad': 0, 'r': 15, 't': 15}
    plotly_fig.layout.xaxis1.tickfont.size = 15
    plotly_fig.layout.xaxis1.titlefont.size = 18
    plotly_fig.layout.yaxis1.tickfont.size = 15
    plotly_fig.layout.yaxis1.titlefont.size = 18
    plotly_fig.layout.xaxis.autorange = True
    if y_type in ['attenuation', 'transmission']:
        plotly_fig['layout']['yaxis']['autorange'] = False
        if plot_scale in ['logy', 'loglog']:
            plot_scale = 'linear'
    else:
        plotly_fig['layout']['yaxis']['autorange'] = True

    if plot_scale == 'logx':
        plotly_fig['layout']['xaxis']['type'] = 'log'
        plotly_fig['layout']['yaxis']['type'] = 'linear'
        plotly_fig['layout']['yaxis']['range'] = [-0.05, 1.05]
    elif plot_scale == 'logy':
        if y_type not in ['attenuation', 'transmission']:
            plotly_fig['layout']['xaxis']['type'] = 'linear'
            plotly_fig['layout']['yaxis']['type'] = 'log'
    elif plot_scale == 'loglog':
        if y_type not in ['attenuation', 'transmission']:
            plotly_fig['layout']['xaxis']['type'] = 'log'
            plotly_fig['layout']['yaxis']['type'] = 'log'
    else:
        plotly_fig['layout']['xaxis']['type'] = 'linear'
        plotly_fig['layout']['yaxis']['type'] = 'linear'
        plotly_fig['layout']['yaxis']['range'] = [-0.05, 1.05]
    return plotly_fig


# Plot control buttons
plot_option_div = html.Div(
    [
        html.Hr(),
        html.H3('Result'),
        html.H5('Plot:'),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div([
                            html.P('X options: '),
                            dcc.RadioItems(id='x_type',
                                           options=[
                                               {'label': ' Energy (eV)', 'value': 'energy'},
                                               {'label': ' Wavelength (\u212B)', 'value': 'lambda'},
                                               {'label': ' Time-of-flight (\u03BCs)', 'value': 'time'},
                                           ],
                                           value='energy',
                                           # n_clicks_timestamp=0,
                                           )
                        ]),
                    ], width=3),
                dbc.Col(
                    [
                        html.Div([
                            html.P('Y options: '),
                            dcc.RadioItems(id='y_type',
                                           options=[
                                               {'label': " Transmission", 'value': 'transmission'},
                                               {'label': ' Attenuation             ', 'value': 'attenuation'},
                                               {'label': ' Attenuation coefficient ', 'value': 'mu_per_cm'},
                                               {'label': " Cross-section (weighted)", 'value': 'sigma'},
                                               {'label': ' Cross-section (raw)     ', 'value': 'sigma_raw'},
                                           ],
                                           value='transmission',
                                           # inline=False
                                           # n_clicks_timestamp=0,
                                           )
                        ]),
                    ], width=3),
                dbc.Col(
                    [
                        html.Div([
                            html.P('Scale options: '),
                            dcc.RadioItems(id='plot_scale',
                                           options=[
                                               {'label': 'Linear', 'value': 'linear'},
                                               {'label': 'Log x', 'value': 'logx'},
                                               {'label': 'Log y', 'value': 'logy'},
                                               {'label': 'Loglog', 'value': 'loglog'},
                                           ],
                                           value='linear',
                                           # n_clicks_timestamp=0,
                                           )
                        ]),
                    ], width=3),
                dbc.Col(
                    [
                        html.Div([
                            html.P('Show options: '),
                            dcc.Checklist(id='show_opt',
                                          options=[
                                              {'label': ' Total', 'value': 'total'},
                                              {'label': ' Layer', 'value': 'layer'},
                                              {'label': ' Element', 'value': 'ele'},
                                              {'label': ' Isotope', 'value': 'iso'},
                                          ],
                                          value=['layer'],
                                          # n_clicks_timestamp=0,
                                          ),
                        ]),
                    ], width=2,
                ),
            ],
        ),
    ],
),

bragg_plot_option_div = html.Div(
    [
        html.Hr(),
        html.H3('Plot:'),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div([
                            html.P('X options: '),
                            dcc.RadioItems(id='x_type',
                                           options=[
                                               {'label': 'Wavelength (\u212B)', 'value': 'lambda'},
                                               {'label': 'Energy (eV)', 'value': 'energy'},
                                           ],
                                           value='lambda',
                                           inline=False,
                                           )
                        ]),
                    ], width=3),
                dbc.Col(
                    [
                        html.Div([
                            html.P('Y options: '),
                            dcc.RadioItems(id='y_type',
                                           options=[
                                               # {'label': 'Transmission', 'value': 'transmission'},
                                               # {'label': 'Attenuation', 'value': 'attenuation'},
                                               # {'label': 'Attenuation coefficient', 'value': 'mu_per_cm'},
                                               # {'label': "Cross-section (weighted)", 'value': 'sigma'},
                                               {'label': 'Cross-section (raw)', 'value': 'sigma_raw'},
                                           ],
                                           value='sigma_raw',
                                           )
                        ]),
                    ], width=3
                ),
                dbc.Col(
                    [
                        html.Div([
                            html.P('Scale options: '),
                            dcc.RadioItems(id='plot_scale',
                                           options=[
                                               {'label': 'Linear', 'value': 'linear'},
                                               {'label': 'Log x', 'value': 'logx'},
                                               {'label': 'Log y', 'value': 'logy'},
                                               {'label': 'Loglog', 'value': 'loglog'},
                                           ],
                                           value='linear',
                                           # n_clicks_timestamp=0,
                                           )
                        ]),
                    ], width=3
                ),
                dbc.Col(
                    [
                        html.Div([
                            html.P('Interactions: '),
                            dcc.Checklist(id='xs_type',
                                          options=[
                                              {'label': 'Total', 'value': 'total'},
                                              {'label': 'Absorption', 'value': 'abs'},
                                              {'label': 'Coherent elastic scattering', 'value': 'coh_el'},
                                              {'label': 'Coherent inelastic scattering', 'value': 'coh_inel'},
                                              {'label': 'Incoherent elastic scattering', 'value': 'inc_el'},
                                              {'label': 'Incoherent inelastic scattering', 'value': 'inc_inel'},
                                          ],
                                          value=['total'],
                                          # n_clicks_timestamp=0,
                                          )
                        ]),
                    ], width=2
                ),
            ],
        ),
    ]
)
