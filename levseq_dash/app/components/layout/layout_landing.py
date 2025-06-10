import dash_bootstrap_components as dbc
from dash import html

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import vis, widgets


# -------------------------------------------------------
def get_landing_page():
    return html.Div(  # TODO: dbc.Container doesn't pick up the fluid container from parent
        [
            # dbc.Row(
            #     [
            #         dbc.Col(
            #             [
            #                 dbc.Card(
            #                     [
            #                         dbc.CardHeader("All Substrate", className=vis.top_card_head),
            #                         dbc.CardBody(
            #                             [
            #                                 html.Div(
            #                                     html.Img(
            #                                         id="id-lab-substrate",
            #                                         style={"maxWidth": "auto", "height": "auto"},
            #                                     ),
            #                                     style={
            #                                         "display": "flex",
            #                                         "justifyContent": "center",
            #                                         "alignItems": "center",
            #                                     },
            #                                 )
            #                             ],
            #                             className=vis.top_card_body
            #                         ),
            #                     ],
            #                     style=vis.card_shadow,
            #                 ),
            #             ],
            #             style=vis.border_column
            #         )
            #     ],
            #     style=vis.border_row
            # ),
            # all the product molecules from mols to grid
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.Div(
                                html.Img(
                                    id="id-lab-substrate",
                                    # TODO: does maxwidth auto make a difference
                                    style={"maxWidth": "100%", "height": "100%"},
                                ),
                                style={
                                    "display": "flex",
                                    "justifyContent": "center",
                                    "alignItems": "center",
                                },
                            ),
                        ],
                        title="Visualization of Substrates Across All Experiments",
                        style=vis.card_shadow,
                    )
                ],
                start_collapsed=True,
                flush=True,
                className="g-0 mt-4 mb-4 fw-bold custom-accordion",
            ),
            # all the product molecules from mols to grid
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.Div(
                                html.Img(
                                    id="id-lab-product",
                                    style={"maxWidth": "auto", "height": "auto"},
                                ),
                                style={
                                    "display": "flex",
                                    "justifyContent": "center",
                                    "alignItems": "center",
                                },
                            ),
                        ],
                        title="Visualization of Products Across all Experiments ",
                        style=vis.card_shadow,
                    )
                ],
                start_collapsed=True,
                flush=True,
                className="g-0 mt-4 mb-4 fw-bold custom-accordion",
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
                                                [widgets.get_table_all_experiments()],
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
