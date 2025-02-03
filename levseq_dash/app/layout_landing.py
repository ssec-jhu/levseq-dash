import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import dcc, html

from levseq_dash.app import components, inline_styles
from levseq_dash.app import global_strings as gs

# -------------------------------------------------------
layout = html.Div(  # TODO: dbc.Container doesn't pick up the fluid container from parent
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Total Experiments", className=inline_styles.top_card_head),
                            dbc.CardBody(id="id-lab-experiment-count", className=inline_styles.top_card_body),
                        ],
                        style=inline_styles.card_shadow,
                    ),
                    width=2,
                    style=inline_styles.border_column,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Used CAS", className=inline_styles.top_card_head),
                            dbc.CardBody(id="id-lab-experiment-all-cas", className=inline_styles.top_card_body),
                        ],
                        style=inline_styles.card_shadow,
                    ),
                    width=5,
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
                                dbc.CardHeader("All Experiments", className=inline_styles.top_card_head),
                                dbc.CardBody(
                                    [
                                        html.Div(  # TODO: dbc.container adds padding to the surrounding area
                                            [
                                                dag.AgGrid(
                                                    id="id-table-all-experiments",
                                                    # rowData=data.to_dict("records"),
                                                    columnDefs=components.get_all_experiments_column_defs(),
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
                                                        "flex": 1,  # TODO: remove this after you put fixed width
                                                    },
                                                    columnSize="sizeToFit",
                                                    # style={"height": "600px", "width": "100%"},
                                                    # style={"width": "100%"},
                                                    dashGridOptions={
                                                        "rowSelection": "multiple",  # Enable multiple selection
                                                        "suppressRowClickSelection": True,
                                                        # Use only checkboxes for selection
                                                        "animateRows": True,
                                                    },
                                                )
                                            ],
                                            className="dbc dbc-ag-grid",
                                            style=inline_styles.border_table,
                                        ),
                                        # TODO: delete this later
                                        html.Br(),
                                        dbc.Alert(
                                            id="id-selected-row-info",
                                            color="secondary",
                                            className="text-center",
                                            style={"fontWeight": "bold"},
                                        ),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "Delete Experiment",
                                                    id="id-button-delete-experiment",
                                                    n_clicks=0,
                                                    disabled=True,
                                                    color="danger",
                                                    className="me-2",
                                                ),
                                                dbc.Button(
                                                    "Go to Experiment",
                                                    id="id-button-show-experiment",
                                                    n_clicks=0,
                                                    disabled=True,
                                                    color="primary",
                                                ),
                                            ],
                                            className="text-center",
                                        ),
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
                        # html.Div(id="selected-row-value"),
                    ],
                    # width=6,
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
