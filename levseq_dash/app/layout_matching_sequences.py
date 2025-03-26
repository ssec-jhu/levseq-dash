import dash_bootstrap_components as dbc
from dash import html

from levseq_dash.app import components, vis
from levseq_dash.app import global_strings as gs


def get_seq_align_form():
    return html.Div(
        [
            dbc.Row(
                [
                    components.get_label_fixed_for_form(gs.seq_align_form_input),
                    dbc.Col(
                        [
                            dbc.Textarea(
                                id="id-input-query-sequence",
                                value=gs.seq_align_form_input_sequence_default,
                                placeholder=gs.seq_align_form_placeholder,
                                debounce=True,
                                style={"width": "100%", "height": "100px"},
                                className="dbc",
                            ),
                        ]
                    ),
                ],
                className="mb-1",
                style=vis.border_row,
            ),
            dbc.Row(
                [
                    components.get_label_fixed_for_form(gs.seq_align_form_threshold),
                    dbc.Col(
                        [
                            dbc.Input(
                                id="id-input-query-sequence-threshold",
                                value=gs.seq_align_form_threshold_default,
                                type="text",
                                debounce=True,
                            ),
                        ],
                        width=2,
                    ),
                ],
                className="mb-1",
                style=vis.border_row,
            ),
            dbc.Row(
                [
                    components.get_label_fixed_for_form(gs.seq_align_form_hot_cold),
                    dbc.Col(
                        [
                            dbc.Input(
                                id="id-input-num-hot-cold",
                                value=gs.seq_align_form_hot_cold_n,
                                type="text",
                                debounce=True,
                            ),
                        ],
                        width=2,
                    ),
                ],
                className="mb-1",
                style=vis.border_row,
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            id="id-button-run-seq-matching",
                            n_clicks=0,
                            className="btn-primary",
                            size="md",
                            children=gs.seq_align_form_button_sequence_matching,
                        ),
                        # button fills the space
                        className="d-grid gap-2 mx-auto",
                    ),
                ],
                className="mt-5 mb-5",
            ),
        ],
        style={
            "width": "60%",  # % width of the div
            "margin": "0 auto",
        },
    )


def get_seq_align_layout():
    return html.Div(
        [
            dbc.Row(
                [html.P(gs.seq_align_blurb)],
                className="mb-4 mt-4",  # add some margin to the top and bottom
            ),
            # the form row
            dbc.Row(
                [
                    dbc.Col(
                        [get_seq_align_form()],
                    ),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            # TODO: maybe make this an html.P
                                            html.Br(),
                                            html.H5(id="id-div-matched-sequences-info"),
                                            html.Br(),
                                            html.Div(
                                                [components.get_table_matched_sequences()],
                                                className="dbc dbc-ag-grid",
                                            ),
                                        ],
                                        className="p-1 mt-3",  # fits to the card border
                                    ),
                                ],
                                className="d-flex flex-column",  # Flexbox for vertical stacking
                                style={
                                    "box-shadow": "1px 2px 7px 0px grey",
                                    "border-radius": "5px",
                                    "height": vis.seq_match_card_height,
                                },
                            ),
                        ],
                        width=8,
                        style=vis.border_column,
                        # remove all gutters from the col to snap to the card
                        # className="g-3"
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.Br(),
                                            html.H5(
                                                id="id-div-selected-matched-sequence-info", style={"whiteSpace": "pre"}
                                            ),
                                            html.Br(),
                                            html.Div(id="id-viewer-temp"),
                                        ],
                                        className="p-1 mt-3",  # fits to the card border
                                    ),
                                ],
                                className="d-flex flex-column",  # Flexbox for vertical stacking
                                style={
                                    "box-shadow": "1px 2px 7px 0px grey",
                                    "border-radius": "5px",
                                    "height": vis.seq_match_card_height,
                                },
                            ),
                        ],
                        style=vis.border_column,
                    ),
                ],
                className="g-2 mt-4 mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.H4("TBD some title? some info?"),
                                            html.Br(),
                                            html.Div(
                                                [components.get_table_matched_sequences_exp_hot_cold_data()],
                                                className="dbc dbc-ag-grid",
                                                # style=vis.border_table,
                                            ),
                                        ],
                                        className="p-1 mt-3",  # fits to the card border
                                        # style={"height": "100%", "overflowX": "auto"}  # Allow content to expand
                                    ),
                                ],
                                className="d-flex flex-column",  # Flexbox for vertical stacking
                                style=vis.card_shadow,
                            ),
                        ],
                        style=vis.border_column,
                    ),
                ],
                className="mt-4 mb-4",
            ),
        ],
    )
