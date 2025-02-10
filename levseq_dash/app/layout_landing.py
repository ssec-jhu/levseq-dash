import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import html
from dash_iconify import DashIconify

from levseq_dash.app import components, inline_styles

MEDIUM = 20
SMALL = 16

del_exp = html.I(
    DashIconify(icon="fa-solid:trash-alt", height=SMALL, width=SMALL),
    # style={"margin-right": "8px"} # add the margin if there is text next to it
    # style={"color": "var(--bs-danger)"}
)
go_to_next = html.I(
    DashIconify(icon="line-md:chevron-small-triple-right", height=SMALL, width=SMALL), style={"margin-left": "8px"}
)
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
            className="g-2 mb-4",
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
                                                        # "flex": 1,  # TODO: remove this after you put fixed width
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
                                        # html.Br(),
                                        # dbc.Alert(
                                        #     id="id-selected-row-info",
                                        #     color="secondary",
                                        #     className="text-center",
                                        #     style={"fontWeight": "bold"},
                                        # ),
                                        html.Br(),
                                        # html.Div(
                                        #     [
                                        #
                                        # dbc.Button( id="id-button-delete-experiment", n_clicks=0,
                                        # children=html.Span([del_exp, "Delete Experiment"]), # since this button is
                                        # a dynamic component that is added to the layout, # the display changes
                                        # override the style={"color": "var(--bs-secondary)"} properties,
                                        # but defining it as a class in assets seems to do the trick. #
                                        # class_name="del-button", # size="sm", class_name="gap-2 col-2 btn-dark",
                                        # className="me-2 btn-lg col-3", ), dbc.Button( children=html.Span(["Go to
                                        # Experiment Dashboard", go_to_next]), id="id-button-show-experiment",
                                        # n_clicks=0, disabled=True, class_name="gap-2 col-2 btn-primary", ), ],
                                        # className="text-center", ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Button(
                                                        id="id-button-delete-experiment",
                                                        n_clicks=0,
                                                        # children=html.Span([del_exp, "Delete Experiment"]),
                                                        children=html.Span(
                                                            [del_exp],
                                                            # override the button color
                                                            # since it's of type "link"
                                                            style={"color": "var(--bs-danger)"},
                                                        ),
                                                        # since this button is a dynamic component that is added to
                                                        # the layout, the display changes override the style={
                                                        # "color": "var(--bs-secondary)"} properties, but defining it
                                                        # as a class in assets seems to do the trick.
                                                        color="link",  # Removes background color
                                                    ),
                                                    width="auto",
                                                ),
                                                dbc.Col(
                                                    dbc.Button(
                                                        children=html.Span(["Go to Experiment Dashboard", go_to_next]),
                                                        id="id-button-show-experiment",
                                                        n_clicks=0,
                                                        disabled=True,
                                                        class_name="btn-primary",
                                                    ),
                                                    width="auto",
                                                    className="text-end",
                                                ),
                                            ],
                                            justify="between",
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
