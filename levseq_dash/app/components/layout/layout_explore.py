import dash_bootstrap_components as dbc
from dash import dcc, html

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import vis, widgets
from levseq_dash.app.components.widgets import get_download_text_icon_combo


# -------------------------------------------------------
def get_layout():
    return html.Div(  # TODO: dbc.Container doesn't pick up the fluid container from parent
        [
            html.Div(
                [
                    html.H4(gs.lab_exp, className="page-title"),
                    html.Hr(),
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [widgets.get_table_all_experiments()],
                                        className="dbc dbc-ag-grid",
                                        style=vis.border_table,
                                    ),
                                    html.Br(),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Button(
                                                    id="id-button-delete-experiment",
                                                    n_clicks=0,
                                                    # children=html.Span([del_exp, "Delete Experiment"]),
                                                    children=html.Span(
                                                        [vis.get_icon(vis.icon_del_exp)],
                                                        # override the button color
                                                        # since it's of type "link"
                                                        style={"color": "var(--bs-danger)"},
                                                    ),
                                                    # since this button is a dynamic component that is added to
                                                    # the layout, the display changes override the style={
                                                    # "color": "var(--bs-secondary)"} properties,
                                                    # but defining it as a class in assets
                                                    # seems to do the trick.
                                                    color="link",  # Removes background color
                                                ),
                                                width=1,
                                            ),
                                            dbc.Col(
                                                html.Div(
                                                    [
                                                        dbc.Button(
                                                            children=[
                                                                get_download_text_icon_combo(
                                                                    "Download Selected Experiment(s)"
                                                                )
                                                            ],
                                                            id="id-button-download-all-experiments",
                                                            n_clicks=0,
                                                            disabled=True,
                                                            # me-2 will add a little space between the buttons
                                                            className="col-4 shadow-sm me-2",
                                                        ),
                                                        dbc.Button(
                                                            children=html.Span(
                                                                [
                                                                    html.Span(gs.go_to),
                                                                    html.Span(
                                                                        vis.get_icon(vis.icon_go_to_next),
                                                                        style={"marginLeft": "8px"},
                                                                    ),
                                                                ]
                                                            ),
                                                            id="id-button-goto-experiment",
                                                            n_clicks=0,
                                                            disabled=True,
                                                            className="col-4 shadow-sm",
                                                        ),
                                                    ],
                                                    className="d-flex justify-content-center",
                                                ),
                                                width=10,
                                            ),
                                            dbc.Col(width=1),  # Empty column for balance
                                        ],
                                        className="mb-1",
                                    ),
                                ],
                                className="p-1",  # fits to the card border
                            ),
                        ],
                        style={
                            "box-shadow": "1px 2px 7px 0px grey",
                            "border-radius": "5px",
                            # "width": "530px", "height": "630px"
                        },
                        #  border-0 removes the hard border
                        # className="shadow border",
                    ),
                    html.Div(
                        id="id-alert-explore",
                        className="mt-3 d-flex justify-content-center",
                    ),
                ],
                className="mb-4",
            ),
            # Confirmation modal for deletion
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Confirm Deletion")),
                    dbc.ModalBody(id="id-delete-modal-body"),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Cancel",
                                id="id-delete-modal-cancel",
                                className="me-2",
                                n_clicks=0,
                            ),
                            dbc.Button(
                                "Delete",
                                id="id-delete-modal-confirm",
                                color="danger",
                                n_clicks=0,
                            ),
                        ]
                    ),
                ],
                id="id-delete-confirmation-modal",
                is_open=False,
                centered=True,
            ),
            # Download component for ZIP files
            dcc.Download(id="id-download-all-experiments-zip"),
        ],
        className=vis.main_page_class,
    )
