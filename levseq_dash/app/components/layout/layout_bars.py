import dash_bootstrap_components as dbc
from dash import html

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import vis


def get_navbar():
    return html.Div(
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Span(vis.get_icon(vis.icon_menu), id="id-menu-icon", className="hamburger_menu"),
                            ],
                            width=1,
                            style=vis.border_column,
                            # justify the menu item all the way to the left
                            className="d-flex align-items-center justify-content-start",
                        ),
                        dbc.Col(
                            [
                                html.Img(
                                    src="../../assets/Caltech Logo 2017/LOGO-WHITE/LOGO-WHITE-RGB/Caltech_LOGO-WHITE"
                                    "-RGB.png",
                                    width="80%",
                                ),
                            ],
                            width=2,
                            style=vis.border_column,
                            # justify to the left of the column (start)
                            className="d-flex align-items-center justify-content-start",
                        ),
                        dbc.Col(
                            [gs.web_title],
                            style=vis.border_column,
                            # center the title
                            className="display-4 d-flex align-items-center justify-content-center",
                        ),
                        dbc.Col(
                            [html.Img(src="../../assets/SSEC_horizontal_white_cropped.png", width="60%")],
                            width=3,
                            style=vis.border_column,
                            # justify the logo to the right (end)
                            className="d-flex align-items-center justify-content-end",
                        ),
                    ],
                    # keep this at 0, increasing this will push the logos out
                    className="g-0",
                    style=vis.border_row,
                ),
            ],
            fluid=True,
            # this will be the height or depth of the top bar
            # class_name="py-5",
        ),
        style={"box-shadow": "0 5px 5px -5px #333"},
        className="bg-primary custom_navbar text-light p-1 text-center fs-1 fw-light border-bottom",  # Div
    )


def get_sidebar():
    return html.Div(
        [
            html.Div(  # don't make this a db.nav
                [
                    dbc.NavLink(
                        [
                            html.Span(vis.get_icon(vis.icon_home), className="custom-nav-icon"),
                            html.Span(gs.nav_lab, className="custom-nav-text"),
                        ],
                        active="exact",
                        href="/",
                        className="custom-nav-item",
                    ),
                    dbc.NavLink(
                        [
                            html.Span(vis.get_icon(vis.icon_upload), className="custom-nav-icon"),
                            html.Span(gs.nav_upload, className="custom-nav-text"),
                        ],
                        active="exact",
                        href=gs.nav_upload_path,
                        className="custom-nav-item",
                    ),
                    dbc.NavLink(
                        [
                            html.Span(vis.get_icon(vis.icon_search), className="custom-nav-icon"),
                            html.Span(gs.nav_find_seq, className="custom-nav-text"),
                        ],
                        active="exact",
                        href=gs.nav_find_seq_path,
                        className="custom-nav-item",
                    ),
                    dbc.NavLink(
                        [
                            html.Span(vis.get_icon(vis.icon_database), className="custom-nav-icon"),
                            html.Span(gs.nav_explore, className="custom-nav-text"),
                        ],
                        active="exact",
                        href=gs.nav_explore_path,
                        className="custom-nav-item",
                    ),
                    dbc.NavLink(
                        [
                            html.Span(vis.get_icon(vis.icon_about), className="custom-nav-icon"),
                            html.Span(gs.nav_about, className="custom-nav-text"),
                        ],
                        active="exact",
                        href=gs.nav_about_path,
                        className="custom-nav-item",
                    ),
                ],
            ),
        ],
        id="id-sidebar",
        className="thin-sidebar collapsed",
    )


# def get_navbar():
#     return dbc.Navbar(
#         dbc.Container(
#             [
#                 dbc.Row(
#                     [
#                         dbc.Col(
#                             [
#                                 # html.Img(src="assets/caltech-new-logo.png", width="70%")
#                             ],
#                             width=2,
#                             style=vis.border_column,
#                             className="d-flex align-items-center justify-content-start",
#                         ),
#                         dbc.Col(
#                             [
#                                 # "Levseq Dashboard"
#                             ],
#                             className="display-4 text-light d-flex align-items-center justify-content-center",
#                         ),
#                         dbc.Col(
#                             [
#                                 # html.Img(src="assets/SSEC_horizontal_white_cropped.png", width="70%")
#                             ],
#                             width=3,
#                             className="d-flex align-items-center justify-content-end",
#                         ),
#                     ],
#                     justify="between",
#                     class_name="g-2",
#                     style=vis.border_row,
#                 ),
#                 # html.Img(src="https://via.placeholder.com/150", height="40px"),
#             ],
#             fluid=True,
#             # this will be the height or depth of the top bar
#             class_name="py-5",
#         ),
#         color="dark",
#         dark=True,
#         # add some margin to the bottom to create some distance.
#         # we can change this number as we progress
#         className="mb-5 border-bottom",
#     )
#
#
# def get_sidebar():
#     return html.Div(
#         [
#             html.Img(
#                 src="https://via.placeholder.com/150",  # Placeholder for the logo
#                 style={"width": "100%", "margin-bottom": "20px"},
#             ),
#             html.Hr(),
#             html.Br(),
#             dbc.Nav(
#                 [
#                     dbc.NavLink(
#                         [vis.icon_home, " Lab Dashboard"],
#                         href="/",
#                         active="exact",
#                         className="sidebar-link",
#                     ),
#                     dbc.NavLink(
#                         [vis.icon_upload, " Upload New Experiment"],
#                         href="/upload",
#                         active="exact",
#                         className="sidebar-link",
#                     ),
#                 ],
#                 vertical=True,
#                 # pills=True,
#             ),
#         ],
#         style={
#             # "background-color": "#f8f9fa",
#             "height": "100%",
#             "padding": "50px",
#         },
#         className="p-0",
#     )
