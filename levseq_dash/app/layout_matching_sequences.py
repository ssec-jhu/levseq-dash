import dash_bootstrap_components as dbc
from dash import dcc, html

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
            # these results will appear/clear
            html.Div(
                id="id-div-seq-alignment-results",
                # TODO: integrate this with clearing results boolean later
                # style={**vis.section_vis},
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Matched Experiments"),
                                            dbc.CardBody(
                                                [
                                                    dbc.Row(
                                                        [
                                                            # this info icon uses markdown in the tooltip so we
                                                            # must allow html and set the flag to true
                                                            html.Div(
                                                                [
                                                                    components.get_info_icon_tooltip_bundle(
                                                                        info_icon_id="id-info-1",
                                                                        help_string=gs.markdown_note_matched_seq,
                                                                        location="top",
                                                                        allow_html=True,
                                                                    ),
                                                                    html.P(
                                                                        id="id-div-matched-sequences-info",
                                                                        className="fw-bolder",
                                                                    ),
                                                                ],
                                                                style={"display": "flex", "gap": "5px"},
                                                            ),
                                                        ],
                                                    ),
                                                    dbc.Row(
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
                                            dbc.CardHeader("Visualize Selected Experiment"),
                                            dbc.CardBody(
                                                [
                                                    dcc.Markdown(
                                                        id="id-div-selected-matched-sequence-info",
                                                        # style={"whiteSpace": "pre"}
                                                    ),
                                                    html.Br(),
                                                    html.Div(id="id-viewer-selected-seq-matched-protein"),
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
                                            dbc.CardHeader("Hot and Cold residues"),
                                            dbc.CardBody(
                                                [
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                components.get_button_download(
                                                                    "id-button-download-hot-cold-results"
                                                                ),
                                                                width=2,
                                                                align="center",
                                                                style=vis.border_column,
                                                            ),
                                                            dbc.Col(
                                                                components.get_radio_items_download_options(
                                                                    "id-button-download-hot-cold-results-options"
                                                                ),
                                                                width=3,
                                                                align="center",
                                                                style=vis.border_column,
                                                            ),
                                                        ],
                                                        className="mb-2 g-1",
                                                    ),
                                                    dbc.Row(
                                                        [components.get_table_matched_sequences_exp_hot_cold_data()],
                                                        className="dbc dbc-ag-grid",
                                                        # style=vis.border_table,
                                                    ),
                                                ],
                                                className="p-1 mt-3",  # fits to the card border
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
            ),
        ],
    )
