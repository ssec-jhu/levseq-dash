import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_molstar
from dash import html

from levseq_dash.app import components, inline_styles
from levseq_dash.app import global_strings as gs

# exp = experiment_2

# -------------------------------------------------------
layout = html.Div(  # TODO: dbc.Container doesn't pick up the fluid container from parent
    [
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(gs.experiment, className=inline_styles.top_card_head),
                            dbc.CardBody(id="id-experiment-name", className=inline_styles.top_card_body),
                        ],
                        style=inline_styles.card_shadow,
                    ),
                    width=2,
                    style=inline_styles.border_column,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(gs.sequence, className=inline_styles.top_card_head),
                            dbc.CardBody(id="id-experiment-sequence", className=inline_styles.top_card_body),
                        ],
                        style=inline_styles.card_shadow,
                    ),
                    width=10,
                    style=inline_styles.border_column,
                ),
            ],
            className="g-3 mb-4",
            style=inline_styles.border_row,
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(gs.technique, className=inline_styles.top_card_head),
                            dbc.CardBody(id="id-experiment-mutagenesis-method", className=inline_styles.top_card_body),
                        ],
                        style=inline_styles.card_shadow,
                        # className="shadow"
                    ),
                    width=2,
                    style=inline_styles.border_column,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(gs.date, className=inline_styles.top_card_head),
                            dbc.CardBody(id="id-experiment-date", className=inline_styles.top_card_body),
                        ],
                        style=inline_styles.card_shadow,
                    ),
                    width=2,
                    style=inline_styles.border_column,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(gs.plates_count, className=inline_styles.top_card_head),
                            dbc.CardBody(id="id-experiment-plate-count", className=inline_styles.top_card_body),
                        ],
                        style=inline_styles.card_shadow,
                    ),
                    width=2,
                    style=inline_styles.border_column,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(gs.substrate_cas, className=inline_styles.top_card_head),
                            dbc.CardBody(id="id-experiment-sub-cas", className=inline_styles.top_card_body),
                        ],
                        style=inline_styles.card_shadow,
                    ),
                    width=2,
                    style=inline_styles.border_column,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(gs.product_cas, className=inline_styles.top_card_head),
                            dbc.CardBody(id="id-experiment-product-cas", className=inline_styles.top_card_body),
                        ],
                        style=inline_styles.card_shadow,
                    ),
                    width=2,
                    style=inline_styles.border_column,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(gs.assay, className=inline_styles.top_card_head),
                            dbc.CardBody(id="id-experiment-assay", className=inline_styles.top_card_body),
                        ],
                        style=inline_styles.card_shadow,
                    ),
                    width=2,
                    style=inline_styles.border_column,
                ),
            ],
            className="g-3 mb-4",
            style=inline_styles.border_row,
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.viewer_header),
                                dbc.CardBody(
                                    [
                                        dash_molstar.MolstarViewer(
                                            id="id-viewer",
                                            # data=data,
                                            style={"width": "auto", "height": "600px"},
                                            layout={
                                                "layoutShowControls": False,
                                                "layoutIsExpanded": False,
                                                # TODO: do we want this option to be true?
                                            },
                                        )
                                    ],
                                    style={
                                        "height": "100%",
                                        "overflowX": "auto",  # Allow content to expand
                                    },
                                ),
                            ],
                            className="d-flex flex-column",  # Flexbox for vertical stacking
                            style=inline_styles.card_shadow,
                        ),
                    ],
                    width=5,
                    style=inline_styles.border_column,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.data_header),
                                dbc.CardBody(
                                    [
                                        html.Div(  # TODO: dbc.container adds padding to the surrounding area
                                            [
                                                # components.get_table(exp.data_df,
                                                #                  components.get_top_variant_column_defs())
                                                dag.AgGrid(
                                                    id="id-table-top-variants",
                                                    # rowData=data.to_dict("records"),
                                                    columnDefs=components.get_top_variant_column_defs(),
                                                    # TODO: update this correctly
                                                    defaultColDef={
                                                        # do NOT set "flex": 1 in default col def as it overrides all
                                                        # the column widths
                                                        "sortable": True,
                                                        "resizable": True,
                                                        "filter": True,
                                                        # Set BOTH items below to True for header to wrap text
                                                        "wrapHeaderText": True,
                                                        "autoHeaderHeight": True,
                                                    },
                                                    # columnSize="sizeToFit",
                                                    style={"height": "600px", "width": "100%"},
                                                    dashGridOptions={
                                                        # "rowDragManaged": True,
                                                        # "rowDragEntireRow": True
                                                        "rowSelection": "single",
                                                    },
                                                )
                                            ],
                                            className="dbc dbc-ag-grid",
                                            style=inline_styles.border_table,
                                        )
                                    ],
                                    className="p-1",  # fits to the card border
                                    # style={"height": "100%", "overflowX": "auto"}  # Allow content to expand
                                ),
                            ],
                            # className="d-flex flex-column",  # Flexbox for vertical stacking
                            style={
                                "box-shadow": "1px 2px 7px 0px grey",
                                "border-radius": "5px",
                                # "width": "530px", "height": "630px"
                            },
                        ),
                        html.Div(id="selected-row-value"),
                    ],
                    width=7,
                    style=inline_styles.border_column,
                ),
            ],
            className="mb-4",  # TODO: change gutter to g-1 here? or not
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
