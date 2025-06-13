import dash_bootstrap_components as dbc
from dash import dcc, html

from levseq_dash.app import global_strings as gs
from levseq_dash.app import global_strings_html as gsh
from levseq_dash.app.components import vis, widgets
from levseq_dash.app.components.widgets import generate_label_with_info


def get_seq_align_form():
    return html.Div(
        [
            dbc.Row(
                [
                    widgets.get_label_fixed_for_form(gs.seq_align_form_input),
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
                    widgets.get_label_fixed_for_form(gs.seq_align_form_threshold),
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
                    widgets.get_label_fixed_for_form(gs.seq_align_form_hot_cold),
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
                className="mt-1 mb-5",
            ),
        ],
        style={
            "width": "60%",  # % width of the div
            "margin": "0 auto",
        },
    )


def create_layout_reaction(id_image, id_substrate_smiles, id_product_smiles):
    """
    Produces a specific layout for the reaction image if substrate -> product
    with the substrate and the product smiles strings under the image
    This combo is used in multiple places, so I am putting it in one function
    """
    return html.Div(
        [
            dbc.Row(
                [
                    html.Img(
                        id=id_image,
                        # this will center the image
                        className="mx-auto d-block",
                        # Note: this will make the reaction image width fill the container width
                        # and not overflow so a smaller screen will show the image smaller and a big monitor
                        # will show the image bigger
                        style={"maxWidth": "100%"},
                    ),
                ],
            ),
            # a row under it with the substrate and product smiles at width=6 exactly
            # this will not allow it to stack vertically
            dbc.Row(
                [
                    dbc.Col(
                        [
                            generate_label_with_info(
                                gs.sub_smiles,
                                id_substrate_smiles,
                            )
                        ],
                        # I am setting this to be 6, so they don't
                        # collapse if the whole card flows into the
                        # other row
                        width=6,
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        [
                            generate_label_with_info(
                                gs.prod_smiles,
                                id_product_smiles,
                            )
                        ],
                        width=6,
                        style=vis.border_column,
                    ),
                ],
                className="p-2",
            ),
        ]
    )


def get_se_alignment_results_layout():
    return html.Div(
        id="id-div-seq-alignment-results",
        style=vis.display_none,
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(gs.seg_align_results, className=vis.top_card_head),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    # this info icon uses markdown in the tooltip so we
                                                    # must allow html and set the flag to true
                                                    html.Div(
                                                        [
                                                            widgets.get_info_icon_tooltip_bundle(
                                                                info_icon_id="id-info-1",
                                                                help_string=gsh.markdown_note_matched_seq,
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
                                                [widgets.get_table_matched_sequences()],
                                                className="dbc dbc-ag-grid",
                                            ),
                                        ],
                                        className="p-1 mt-3",  # fits to the card border
                                    ),
                                ],
                                style={
                                    "box-shadow": "1px 2px 7px 0px grey",
                                    "border-radius": "5px",
                                    "height": vis.seq_match_card_height,
                                },
                            ),
                        ],
                        width=7,
                        style=vis.border_column,
                        # remove all gutters from the col to snap to the card
                        # className="g-3"
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(gs.seq_align_visualize, className=vis.top_card_head),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    create_layout_reaction(
                                                        "id-selected-seq-matched-reaction-image",
                                                        "id-selected-seq-matched-substrate",
                                                        "id-selected-seq-matched-product",
                                                    )
                                                ],
                                                className="mb-3",
                                            ),
                                            dbc.Row([html.Div(id="id-viewer-selected-seq-matched-protein")]),
                                        ],
                                        className="p-1 mb-3",  # fits to the card border
                                    ),
                                ],
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
                                    dbc.CardHeader(gs.seq_align_residues, className=vis.top_card_head),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        widgets.get_button_download(
                                                            "id-button-download-hot-cold-results"
                                                        ),
                                                        width=2,
                                                        align="center",
                                                        style=vis.border_column,
                                                    ),
                                                    dbc.Col(
                                                        widgets.get_radio_items_download_options(
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
                                                [widgets.get_table_matched_sequences_exp_hot_cold_data()],
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
    )


def get_seq_align_layout():
    return html.Div(
        [
            html.Div(
                [
                    html.H4(gs.nav_seq, style=vis.level_4_titles),
                    html.Hr(),
                    # add some left and right padding -> px-5
                    html.P(gsh.seq_align_blurb, className="px-5 text-primary text-wrap"),
                ],
                className="p-5",
            ),
            # the form row
            dbc.Row(
                [
                    dbc.Col(
                        [get_seq_align_form()],
                    ),
                ],
            ),
            html.Div(
                id="id-alert-seq-alignment",
                className="d-flex justify-content-center",
            ),
            # these results will appear/clear
            dcc.Loading(
                overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                # overlay_style={  # "display": "block",
                #     "alignItems": "flex-start",
                #     "justifyContent": "center",  # Center horizontally
                #     "position": "absolute",  # the KEY
                #     # "paddingTop": "20px",  # Add space from top
                #     # "zIndex": 1000
                # },
                type="circle",
                color="var(--bs-secondary)",
                # Use the target_components property to specify which component id and component property
                # combinations it wraps can trigger the loading spinner.
                # The spinner component is displayed only when one of the
                # target component and properties enters loading state.
                target_components={"id-table-matched-sequences": "rowData"},
                children=get_se_alignment_results_layout(),
            ),
        ],
    )
