import dash_bootstrap_components as dbc
from dash import dcc, html

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import vis

# -------------------------------------------------------


def get_layout():
    return html.Div(  # TODO: dbc.Container doesn't pick up the fluid container from parent
        [
            dbc.Container(
                [
                    dbc.Row(
                        [
                            html.Img(
                                src="/assets/bg.png",
                                className="bg-image-center bg-image-center-container bg-image-washed",
                            ),
                            html.H1("Welcome to the Levseq Dashboard!", className="fw-bold text-primary text-center"),
                            html.H6(
                                "a visualization tool for analyzing directed "
                                "evolution experiments in protein engineering",
                                className="text-secondary text-center",
                            ),
                        ],
                        className="p-5 d-flex justify-content-center align-items-center",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                action_card(
                                    icon=vis.icon_upload,
                                    label=gs.nav_upload,
                                    href=gs.nav_upload_path,
                                    text_below=gs.small_text_upload,
                                ),
                                md=4,
                                className="mb-4",
                            ),
                            dbc.Col(
                                action_card(
                                    icon=vis.icon_search,
                                    label=gs.nav_find_seq,
                                    href=gs.nav_find_seq_path,
                                    text_below=gs.small_text_find,
                                ),
                                md=4,
                                className="mb-4",
                            ),
                            dbc.Col(
                                action_card(
                                    icon=vis.icon_database,
                                    label=gs.nav_explore,
                                    href=gs.nav_explore_path,
                                    text_below=gs.small_text_explore,
                                ),
                                md=4,
                                className="mb-4",
                            ),
                        ],
                        justify="center",
                    ),
                ],
                className="py-5",
            ),
        ],
        className=vis.main_page_class,
        style={
            # this is very important with the background image
            "zIndex": 1,
        },
    )


def action_card(icon: str, label: str, href: str, text_below: str):
    """Return a clickable action card with an icon and label."""
    card = dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [vis.get_icon(icon, size=vis.LARGE)],
                    # className="icon-style1", style={"color": "white"},
                    className="icon-style3",  # hover creates a background circle shape
                    # className="label-icon-style", # colors everything orange
                ),
                html.H4(
                    label,
                    className="mt-3 fw-semibold text-center",
                    # className="label-icon-style mt-2 fw-semibold text-center"
                ),
                html.Small(text_below, className="text-secondary"),
            ],
            # make sure everything is centered
            className=" text-primary d-flex flex-column align-items-center justify-content-center py-4",
        ),
        # h-100 takes up 100% of the container
        className="card-style rounded-3 h-100 p-3",
    )
    return dcc.Link(
        card,
        href=href,
        className="text-decoration-none",  # remove the hyperlink
    )
