import dash_bootstrap_components as dbc
from dash import html

from levseq_dash.app import vis


def get_navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                # html.Img(src="assets/caltech-new-logo.png", width="70%")
                            ],
                            width=2,
                            style=vis.border_column,
                            className="d-flex align-items-center justify-content-start",
                        ),
                        dbc.Col(
                            [
                                # "Levseq Dashboard"
                            ],
                            className="display-4 text-light d-flex align-items-center justify-content-center",
                        ),
                        dbc.Col(
                            [
                                # html.Img(src="assets/SSEC_horizontal_white_cropped.png", width="70%")
                            ],
                            width=3,
                            className="d-flex align-items-center justify-content-end",
                        ),
                    ],
                    justify="between",
                    class_name="g-2",
                    style=vis.border_row,
                ),
                # html.Img(src="https://via.placeholder.com/150", height="40px"),
            ],
            fluid=True,
            # this will be the height or depth of the top bar
            class_name="py-5",
        ),
        color="dark",
        dark=True,
        # add some margin to the bottom to create some distance.
        # we can change this number as we progress
        className="mb-5 border-bottom",
    )


def get_sidebar():
    return html.Div(
        [
            html.Img(
                src="https://via.placeholder.com/150",  # Placeholder for the logo
                style={"width": "100%", "margin-bottom": "20px"},
            ),
            html.Hr(),
            html.Br(),
            dbc.Nav(
                [
                    dbc.NavLink(
                        [vis.icon_home, " Lab Dashboard"],
                        href="/",
                        active="exact",
                        className="sidebar-link",
                    ),
                    dbc.NavLink(
                        [vis.icon_upload, " Upload New Experiment"],
                        href="/upload",
                        active="exact",
                        className="sidebar-link",
                    ),
                ],
                vertical=True,
                # pills=True,
            ),
        ],
        style={
            # "background-color": "#f8f9fa",
            "height": "100%",
            "padding": "50px",
        },
        className="p-0",
    )
