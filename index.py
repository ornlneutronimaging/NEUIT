from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Output, Input

from apps import resonance, transmission, converter, tof_plotter, bragg, golden_angles, home_page
from config import app_dict
from app import app

image_logo = 'team_logo.png'


header = html.Div([
    dbc.Navbar([
                dbc.Row([
                    dbc.Col([
                        html.A(
                        html.Img(src=app.get_asset_url(image_logo),
                                 height="60px",
                                 ),
                        href="/",
                        )],
                    ),
                    dbc.Col(html.Pre(""),
                            class_name="header_pre_padding"),
                    dbc.Col(html.H5("i"),
                            width="auto",
                            class_name="header_i"),
                    dbc.Col(html.H1("NEU"),
                            width="auto",
                            class_name="header_col_right_padding"),
                    dbc.Col(html.H5("tron"),
                            width="auto",
                            class_name="header_tron"),
                    dbc.Col(html.Pre(""),
                            class_name="header_pre_padding"),
                    dbc.Col(html.H1("I"),
                            class_name="header_col_right_padding"),
                    dbc.Col(html.H5("maging"),
                            class_name="header_col_left_padding_special_case_for_i"),
                    dbc.Col(html.Pre(""),
                            class_name="header_pre_padding"),
                    dbc.Col(html.H1("T"),
                            class_name="header_col_right_padding"),
                    dbc.Col(html.H5("oolbox"),
                            class_name="header_col_left_padding"),
                    dbc.Col(html.Pre(""),
                            class_name="header_dropdown_separator"),
                    ],
                    align="center"),
                dbc.DropdownMenu(
                        label="Select a Tool",
                        id="list_of_tools_dropdown",
                        children=[
                            dbc.DropdownMenuItem("Neutron Transmission", href="/transmission"),
                            dbc.DropdownMenuItem("Neutron Resonance", href="/resonance"),
                            dbc.DropdownMenuItem("Composition Converter", href="/converter"),
                            dbc.DropdownMenuItem("Time of flight plotter", href='/tof_plotter'),
                            dbc.DropdownMenuItem("Bragg edge simulator", href='/bragg'),
                            dbc.DropdownMenuItem("Golden angles", href='/golden_angles'),
                        ],
                        color="primary",
                        size="lg",
                ),
            ],
            class_name="header_format",
            color="white",
        ),
    dcc.Location(id='location'),
    html.Hr(style={'borderTop': '3px solid blue'}),
    html.Div(id='tool_selected_page'),
    html.Div(id='main_content')
])
app.layout = header


@app.callback(Output('main_content', 'children'),
              Input('location', 'pathname'))
def fill_main_content(pathname):
    if pathname is None:
        return "Loading ..."

    for _key in app_dict.keys():
        if app_dict[_key]['url'] == pathname:
            return eval(f"{_key}.layout")
    if pathname == '/':
        return home_page.layout
    else:
        return '404: URL not founds!'


if __name__ == '__main__':
    app.run_server(debug=True)
