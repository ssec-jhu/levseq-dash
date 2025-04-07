import dash_bootstrap_components as dbc
from dash import html

from levseq_dash.app import components, vis
from levseq_dash.app import global_strings as gs


# -------------------------------------------------------
def get_landing_page():
    return html.Div(  # TODO: dbc.Container doesn't pick up the fluid container from parent
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.lab_total, className=vis.top_card_head),
                                dbc.CardBody(id="id-lab-experiment-count", className=vis.top_card_body),
                            ],
                            style=vis.card_shadow,
                        ),
                        width=2,
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.lab_cas, className=vis.top_card_head),
                                dbc.CardBody(id="id-lab-experiment-all-cas", className=vis.top_card_body),
                            ],
                            style=vis.card_shadow,
                        ),
                        # width=5,
                        style=vis.border_column,
                    ),
                ],
                className="g-2 mb-4",
                style=vis.border_row,
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(gs.lab_exp, className=vis.top_card_head),
                                    dbc.CardBody(
                                        [
                                            html.Div(  # TODO: dbc.container adds padding to the surrounding area
                                                [components.get_table_all_experiments()],
                                                className="dbc dbc-ag-grid",
                                                style=vis.border_table,
                                            ),
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
                                            # Experiment Dashboard", go_to_next]), id="id-button-goto-experiment",
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
                                                                [vis.icon_del_exp],
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
                                                        width="auto",
                                                    ),
                                                    dbc.Col(
                                                        dbc.Button(
                                                            children=html.Span([gs.go_to, vis.icon_go_to_next]),
                                                            id="id-button-goto-experiment",
                                                            n_clicks=0,
                                                            disabled=True,
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
                        ],
                        # width=6,
                        style=vis.border_column,
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
