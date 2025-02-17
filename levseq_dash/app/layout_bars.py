import dash_bootstrap_components as dbc
from dash import html

from levseq_dash.app import vis


def get_navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                # Center Title Placeholder
                # html.Div("App Title", className="mx-auto text-center",
                # style={"fontSize": "24px", "fontWeight": "bold"}),
                dbc.NavbarBrand("Levseq Dashboard", className="fs1"),
                # Right Logo Placeholder
                html.Img(src="https://via.placeholder.com/150", height="40px"),
            ],
            className="d-flex justify-content-between align-items-center",
        ),
        color="dark",
        dark=True,
        className="text-light py-4 text-center fs-1 fw-light border-bottom",
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
            "padding": "20px",
        },
        className="p-0",
    )
