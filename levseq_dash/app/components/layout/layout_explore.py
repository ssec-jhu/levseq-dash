import dash_bootstrap_components as dbc
from dash import html

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import vis, widgets


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
                                                width="auto",
                                            ),
                                            dbc.Col(
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
                                                    # size="lg",
                                                    className="shadow-sm",
                                                ),
                                                # width="auto",
                                                # className="text-end",
                                                # button fills the space
                                                className="d-grid gap-2 mx-auto col-5",
                                            ),
                                        ],
                                        justify="between",
                                        className="mb-4",
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
                        #  border-0 removes the hard border
                        # className="shadow border",
                    ),
                ],
                className="mb-4",
            ),
        ],
        className=vis.main_page_class,
    )
