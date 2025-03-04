import dash_bootstrap_components as dbc
from dash import dcc, html

from levseq_dash.app import components, vis
from levseq_dash.app import global_strings as gs


# -------------------------------------------------------
def get_experiment_page():
    return html.Div(  # TODO: dbc.Container doesn't pick up the fluid container from parent
        [
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.sequence, className=vis.top_card_head),
                                dbc.CardBody(id="id-experiment-sequence", className=vis.top_card_body),
                            ],
                            style=vis.card_shadow,
                        ),
                        # width=10,
                        style=vis.border_column,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.experiment, className=vis.top_card_head),
                                dbc.CardBody(id="id-experiment-name", className=vis.top_card_body),
                            ],
                            style=vis.card_shadow,
                        ),
                        width=3,
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.date, className=vis.top_card_head),
                                dbc.CardBody(id="id-experiment-date", className=vis.top_card_body),
                            ],
                            style=vis.card_shadow,
                        ),
                        width=2,
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.upload_date, className=vis.top_card_head),
                                dbc.CardBody(id="id-experiment-upload", className=vis.top_card_body),
                            ],
                            style=vis.card_shadow,
                        ),
                        width=2,
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.technique, className=vis.top_card_head),
                                dbc.CardBody(id="id-experiment-mutagenesis-method", className=vis.top_card_body),
                            ],
                            style=vis.card_shadow,
                            # className="shadow"
                        ),
                        width=3,
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.plates_count, className=vis.top_card_head),
                                dbc.CardBody(id="id-experiment-plate-count", className=vis.top_card_body),
                            ],
                            style=vis.card_shadow,
                        ),
                        width=2,
                        style=vis.border_column,
                    ),
                ],
                className="g-3 mb-4",
                style=vis.border_row,
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.assay, className=vis.top_card_head),
                                dbc.CardBody(id="id-experiment-assay", className=vis.top_card_body),
                            ],
                            style=vis.card_shadow,
                        ),
                        width=3,
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.cas_file, className=vis.top_card_head),
                                dbc.CardBody(id="id-experiment-file-cas", className=vis.top_card_body),
                            ],
                            style=vis.card_shadow,
                        ),
                        width=3,
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.substrate_cas, className=vis.top_card_head),
                                dbc.CardBody(id="id-experiment-sub-cas", className=vis.top_card_body),
                            ],
                            style=vis.card_shadow,
                        ),
                        width=3,
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.product_cas, className=vis.top_card_head),
                                dbc.CardBody(id="id-experiment-product-cas", className=vis.top_card_body),
                            ],
                            style=vis.card_shadow,
                        ),
                        width=3,
                        style=vis.border_column,
                    ),
                ],
                className="g-3 mb-4",
                style=vis.border_row,
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(gs.top_variants, className=vis.top_card_head),
                                    dbc.CardBody(
                                        [
                                            html.Div(  # TODO: dbc.container adds padding to the surrounding area
                                                [components.get_table_experiment()],
                                                className="dbc dbc-ag-grid",
                                                # style=vis.border_table,
                                            )
                                        ],
                                        className="p-1 mt-3",  # fits to the card border
                                        # style={"height": "100%", "overflowX": "auto"}  # Allow content to expand
                                    ),
                                ],
                                # className="d-flex flex-column",  # Flexbox for vertical stacking
                                style={
                                    "box-shadow": "1px 2px 7px 0px grey",
                                    "border-radius": "5px",
                                    # "width": "530px",
                                    # "height": "600px"
                                },
                            ),
                        ],
                        width=6,
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(gs.viewer_header, className=vis.top_card_head),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.Span(
                                                                [
                                                                    dbc.Switch(
                                                                        id="id-switch-residue-view",
                                                                        value=False,
                                                                        # className="fs-5",
                                                                        className="custom-switch",
                                                                    ),
                                                                    dbc.Label(" View all residues"),
                                                                    # dmc.Switch(
                                                                    #     # thumbIcon=vis.icon_eye,
                                                                    #     id="id-switch-residue-view",
                                                                    #     label="View all residues",
                                                                    #     onLabel="ON",#vis.icon_eye_open,
                                                                    #     offLabel="OFF",#vis.icon_eye_closed,
                                                                    #     size="md",
                                                                    #     className="custom-switch",
                                                                    #     checked=False,
                                                                    # )
                                                                ],
                                                                style={"display": "flex"},
                                                            )
                                                        ],
                                                        width=2,
                                                    ),
                                                ],
                                                class_name="mt-3 mb-3",
                                            ),
                                            dbc.Row(dbc.Col(components.get_protein_viewer())),
                                        ],
                                        style={
                                            "height": "100%",
                                            "overflowX": "auto",  # Allow content to expand
                                        },
                                    ),
                                ],
                                className="d-flex flex-column",  # Flexbox for vertical stacking
                                style=vis.card_shadow,
                            ),
                        ],
                        width=6,
                        style=vis.border_column,
                    ),
                ],
                className="mb-4",  # TODO: change gutter to g-1 here? or not
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Heatmap", className=vis.top_card_head),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.Div(
                                                                [
                                                                    dbc.Label("Select Property"),
                                                                    dcc.Dropdown(id="id-list-properties"),
                                                                ],
                                                                className="dbc",
                                                            )
                                                        ],
                                                        style=vis.border_column,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.Div(
                                                                [
                                                                    dbc.Label("Select Plate ID"),
                                                                    dcc.Dropdown(id="id-list-plates"),
                                                                ],
                                                                className="dbc",
                                                            )
                                                        ],
                                                        style=vis.border_column,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.Div(
                                                                [
                                                                    dbc.Label("Select CAS number"),
                                                                    dcc.Dropdown(id="id-list-cas-numbers"),
                                                                ],
                                                                className="dbc",
                                                            )
                                                        ],
                                                        style=vis.border_column,
                                                    ),
                                                ],
                                                className="g-1",
                                            ),
                                            dbc.Row(
                                                [dcc.Graph("id-experiment-heatmap")],
                                                className="mb-4 g-0",
                                                style=vis.border_row,
                                            ),
                                        ],
                                        # keep this at p-1 or 2 so the figure doesn't clamp to the sides of the card
                                        # I have set the margins on that to 0
                                        className="p-2",
                                        style=vis.border_card,
                                    ),
                                ],
                                style={
                                    "box-shadow": "1px 2px 7px 0px grey",
                                    "border-radius": "5px",
                                    # "width": "530px", "height": "630px"
                                },
                            ),
                        ],
                        width=6,
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Fitness Value Ranking", className=vis.top_card_head),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.Div(
                                                                [
                                                                    dbc.Label("Select Plate ID"),
                                                                    dcc.Dropdown(id="id-list-plates-ranking-plot"),
                                                                ],
                                                                className="dbc",
                                                            )
                                                        ],
                                                        style=vis.border_column,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.Div(
                                                                [
                                                                    dbc.Label("Select CAS number"),
                                                                    dcc.Dropdown(id="id-list-cas-numbers-ranking-plot"),
                                                                ],
                                                                className="dbc",
                                                            )
                                                        ],
                                                        style=vis.border_column,
                                                    ),
                                                ],
                                                className="g-1",
                                            ),
                                            dbc.Row(
                                                [dcc.Graph("id-experiment-ranking-plot")],
                                                className="mb-4 g-0",
                                                style=vis.border_row,
                                            ),
                                        ],
                                        # keep this at p-1 or 2 so the figure doesn't clamp to the sides of the card
                                        # I have set the margins on that to 0
                                        className="p-2",
                                        style=vis.border_card,
                                    ),
                                ],
                                style={
                                    "box-shadow": "1px 2px 7px 0px grey",
                                    "border-radius": "5px",
                                    # "width": "530px", "height": "630px"
                                },
                            )
                        ],
                        width=6,
                        style=vis.border_column,
                    ),
                ],
                className="mb-4",
            ),
        ],
        # className="mt-5 mb-5 bg-light"
        # fluid=True,
        className="g-0 p-1 bs-light-bg-subtle",
        style={
            # "width": "90%",  # 50% width
            # "margin": "0 auto",  # Center horizontally
            # "text-align": "center",  # Center text inside the div
            # "border": "1px solid cyan",  # for visual debugging
            # "padding": "10px",  #spacing inside the div
        },
    )
