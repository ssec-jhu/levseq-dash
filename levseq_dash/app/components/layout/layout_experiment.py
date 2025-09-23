import dash_bootstrap_components as dbc
from dash import dcc, html

from levseq_dash.app import global_strings as gs
from levseq_dash.app import global_strings_html as gsh
from levseq_dash.app.components import vis, widgets
from levseq_dash.app.components.widgets import generate_label_with_info


def get_slider_area_layout():
    return dbc.Card(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Span(
                            [
                                dbc.Switch(
                                    id="id-switch-residue-view",
                                    className="custom-switch",
                                    label=gs.view_all,
                                    value=False,
                                    style={"margin-right": "5px"},
                                ),
                                widgets.get_info_icon_tooltip_bundle(
                                    info_icon_id="id-switch-residue-view-info",
                                    help_string=gs.exp_slider_help,
                                    location="top",
                                ),
                            ],
                            className="d-flex",
                        ),
                        width=4,
                        align="center",
                    ),
                    dbc.Col(
                        [gs.select_smiles],
                        # make this test align to the right horizontally
                        # and center it vertically
                        className="m-0 p-0 align-items-center text-end",
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="id-list-smiles-residue-highlight",
                            disabled=True,
                        ),
                        style=vis.border_column,
                    ),
                ],
                align="center",
                class_name="mt-2 px-1",
            ),
            dbc.Row(
                [
                    html.Div(
                        id="id-div-filtered-residue",
                        children="",
                        className="mt-3 text-body fw-bolder",
                    ),
                    dcc.RangeSlider(
                        id="id-slider-ratio",
                        value=[0.5, 2.5],
                        min=0,
                        marks=None,
                        tooltip={
                            "placement": "bottom",
                            "always_visible": True,
                        },
                        className="custom-slider fw-bold mt-3 mb-3",
                        disabled=True,
                    ),
                ],
                style=vis.border_row,
            ),
        ],
        # class_name="border rounded-2",
    )


def get_tab_experiment_main():
    # dbc.Container doesn't pick up the fluid container from parent keep as html.Div
    return html.Div(
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
                                dbc.CardHeader("Experiment Info", className=vis.top_card_head),
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            [
                                                generate_label_with_info(gs.experiment, "id-experiment-name"),
                                                generate_label_with_info(gs.date, "id-experiment-date"),
                                                generate_label_with_info(gs.upload_date, "id-experiment-upload"),
                                                generate_label_with_info(
                                                    gs.technique, "id-experiment-mutagenesis-method"
                                                ),
                                                generate_label_with_info(gs.assay, "id-experiment-assay"),
                                                generate_label_with_info(gs.plates_count, "id-experiment-plate-count"),
                                                generate_label_with_info(gs.smiles_file, "id-experiment-file-smiles"),
                                                generate_label_with_info(
                                                    gs.additional_info, "id-experiment-additional-info"
                                                ),
                                            ],
                                            className="overflow-auto",  # enables scroll if needed
                                            style={
                                                # the smiles strings are very long at times,
                                                # we need them to break if they can to allow
                                                # for the reaction image to the right
                                                # to have space as well
                                                "wordBreak": "break-all",  # this is the key
                                                "whiteSpace": "normal",
                                                # BUT: sometimes the card collapse into 10% width because the reaction
                                                # image is too long, so keep a min width for the info,
                                                # if it doesn't work out let the connects flow into the next row
                                                "minWidth": "150px",
                                                # the smiles strings are too long. Capping out the height,
                                                # so it doesn't create a long card
                                                "maxHeight": "280px",  # limit height of the content
                                            },
                                        )
                                    ],
                                    className=vis.top_card_body,
                                ),
                            ],
                            style=vis.card_shadow,
                        ),
                        # NOTE: if I keep this a fixed width and the reaction images flows over, user will see this
                        # card as a fixed 3 so commenting out, but if you decide to put it back in,  make sure you
                        # set the image below with style={"maxWidth": "100%"}
                        # width=3,
                        # NOTE: allowing the card to flex to
                        # the next row will need a margin for the card, so they don't look like it looks seamless
                        className="mb-3",
                        style=vis.border_column,
                    ),
                    # --------------------------------------
                    # Experiment page reaction image card
                    # --------------------------------------
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.reaction, className=vis.top_card_head),
                                dbc.CardBody(
                                    [
                                        html.Img(
                                            id="id-experiment-reaction-image",
                                            className="mx-auto d-block",  # this will center the image
                                            # NOTE: see comments above regarding below
                                            # style={"maxWidth": "100%"}
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        generate_label_with_info(
                                                            gs.sub_smiles, "id-experiment-substrate"
                                                        )
                                                    ],
                                                    # I am setting this to be 6, so they don't collapse if the whole
                                                    # card flows into the other row
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [generate_label_with_info(gs.prod_smiles, "id-experiment-product")],
                                                ),
                                            ],
                                            style=vis.border_row,
                                            # add some padding around the smiles string area for better aesthetics
                                            className="p-2",
                                        ),
                                    ],
                                    className=vis.top_card_body,
                                ),
                            ],
                            style=vis.card_shadow,
                        ),
                        style=vis.border_column,
                        className="mb-3",
                    ),
                ],
                className="mb-3",
            ),
            # --------------------------------------
            # top variants and viewer row
            # --------------------------------------
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(gs.top_variants, className=vis.top_card_head),
                                    dbc.CardBody(
                                        [
                                            # keep as is,  dbc.container adds padding to the surrounding area
                                            html.Div(
                                                [widgets.get_table_experiment_top_variants()],
                                                className="dbc dbc-ag-grid",
                                                # style=vis.border_table,
                                            )
                                        ],
                                        className="p-1 mt-3",  # fits to the card border
                                        # style={"height": "100%", "overflowX": "auto"}  # Allow content to expand
                                    ),
                                ],
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
                                                [get_slider_area_layout()],
                                                class_name="p-2",
                                            ),
                                            dbc.Row(dbc.Col(widgets.get_protein_viewer())),
                                        ],
                                        # style={
                                        #     "height": "100%",
                                        #     "overflowX": "auto",  # Allow content to expand
                                        # },
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
            # heatmap plot and retention plots
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.well_heatmap, className=vis.top_card_head),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    html.Div(
                                                        [
                                                            dbc.Label(gs.select_property),
                                                            dcc.Dropdown(id="id-list-properties"),
                                                        ],
                                                        className="dbc",
                                                    ),
                                                    style=vis.border_column,
                                                ),
                                                dbc.Col(
                                                    html.Div(
                                                        [
                                                            dbc.Label(gs.select_plate),
                                                            dcc.Dropdown(id="id-list-plates"),
                                                        ],
                                                        className="dbc",
                                                    ),
                                                    style=vis.border_column,
                                                ),
                                                dbc.Col(
                                                    html.Div(
                                                        [
                                                            dbc.Label(gs.select_smiles),
                                                            dcc.Dropdown(id="id-list-smiles"),
                                                        ],
                                                        className="dbc",
                                                    ),
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
                            style=vis.card_shadow,
                        ),
                        width=6,
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.retention_function, className=vis.top_card_head),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    html.Div(
                                                        [
                                                            dbc.Label(gs.select_plate),
                                                            dcc.Dropdown(id="id-list-plates-ranking-plot"),
                                                        ],
                                                        className="dbc",
                                                    ),
                                                    style=vis.border_column,
                                                ),
                                                dbc.Col(
                                                    html.Div(
                                                        [
                                                            dbc.Label(gs.select_smiles),
                                                            dcc.Dropdown(id="id-list-smiles-ranking-plot"),
                                                        ],
                                                        className="dbc",
                                                    ),
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
                            style=vis.card_shadow,
                        ),
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


def get_seq_align_form_exp():
    """
    This is a wrapper function for the form on the Related Variants and Positions Search tab.
    """
    return html.Div(
        [
            dbc.Row(dbc.Label(gs.exp_seq_align_form_input, className="fw-bolder fs-6")),
            dbc.Row(
                [
                    html.Div(
                        id="id-input-exp-related-variants-query-sequence",
                        style={
                            "whiteSpace": "normal",  # ensures wrapping
                            "wordWrap": "break-word",  # breaks long words if needed
                            # to reduce the font size for the sequence here, it's just put for reference so
                            # I am setting it 85% od the root element
                            "fontSize": "0.85rem",
                        },
                        className="text-muted mb-1",
                    ),
                ],
                style=vis.border_row,
            ),
            dbc.Row(
                [
                    widgets.get_label_fixed_for_form(gs.seq_align_form_threshold),
                    dbc.Col(
                        [
                            widgets.get_input_plus_info_ico_bundle(
                                input_id="id-input-exp-related-variants-threshold",
                                input_value=gs.seq_align_form_threshold_default,
                                info_icon_help_string=gs.help_threshold,
                            ),
                        ],
                        width=3,
                    ),
                ],
                style=vis.border_row,
            ),
            dbc.Row(
                [
                    widgets.get_label_fixed_for_form(gs.exp_seq_align_residue),
                    dbc.Col(
                        [
                            widgets.get_input_plus_info_ico_bundle(
                                input_id="id-input-exp-related-variants-residue",
                                input_value="",
                                info_icon_help_string=gs.exp_seq_align_residue_help,
                            ),
                        ],
                        width=3,
                        align="center",
                    ),
                ],
                className="mb-1",
                style=vis.border_row,
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            id="id-button-run-seq-matching-exp",
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
    )


def get_card_experiment_related_variants_result():
    return dbc.Card(
        [
            dbc.CardHeader(gs.exp_seq_align_related_experiments, className=vis.top_card_head),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [generate_label_with_info(gs.exp_seq_align_query_info_2, "id-exp-related-variants-id")],
                                width=6,
                                className="p-1 border-end",
                            ),
                            dbc.Col(
                                [
                                    generate_label_with_info(
                                        gs.exp_seq_align_query_info_1, "id-exp-related-variants-selected-id"
                                    )
                                ],
                                className="p-1",
                            ),
                        ],
                        className="g-1 mt-1 border",
                        style=vis.border_row,
                    ),
                    # -----------------------------
                    # reaction images
                    # -----------------------------
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Img(
                                        id="id-exp-related-variants-reaction-image",
                                        # this will center the image
                                        className="mx-auto d-block",
                                        # Note: this will make the reaction image width fill the container width and
                                        # not overflow so a smaller screen will show the image smaller and a big
                                        # monitor will show the image bigger
                                        # style={"maxWidth": "100%"},
                                        style={
                                            "width": "100%",  # Stretch to column width and do NOT overflow
                                            "objectFit": "contain",  # Fit inside container
                                        },
                                    ),
                                ],
                                width=6,
                                className="border-end",
                            ),
                            dbc.Col(
                                [
                                    html.Img(
                                        id="id-exp-related-variants-selected-reaction-image",
                                        # this will center the image
                                        className="mx-auto d-block",
                                        # Note: this will make the reaction image width fill the container width and
                                        # not overflow so a smaller screen will show the image smaller and a big
                                        # monitor will show the image bigger
                                        style={"maxWidth": "100%"},
                                    ),
                                ],
                            ),
                        ],
                        className="g-1 border border-top-0 border-bottom-0",
                    ),
                    # -----------------------------
                    # substrate and product smiles for experiment and selected match
                    # -----------------------------
                    dbc.Row(
                        [
                            dbc.Col(
                                [generate_label_with_info(gs.sub_smiles, "id-exp-related-variants-substrate")],
                                width=3,
                                className="p-1",
                            ),
                            dbc.Col(
                                [generate_label_with_info(gs.prod_smiles, "id-exp-related-variants-product")],
                                width=3,
                                className="p-1 border-end",
                            ),
                            dbc.Col(
                                [generate_label_with_info(gs.sub_smiles, "id-exp-related-variants-selected-substrate")],
                                width=3,
                                className="p-1",
                            ),
                            dbc.Col(
                                [generate_label_with_info(gs.prod_smiles, "id-exp-related-variants-selected-product")],
                                width=3,
                                className="p-2",
                            ),
                        ],
                        className="g-1 border border-top-0",
                        style=vis.border_row,
                    ),
                    dbc.Row(
                        [
                            # -----------------------------
                            # download button row
                            # -----------------------------
                            dbc.Col(
                                [
                                    widgets.get_download_radio_combo(
                                        "id-button-download-related-variants-results",
                                        "id-button-download-related-variants-results-options",
                                    ),
                                ],
                                width=6,
                                style=vis.border_column,
                            ),
                            dbc.Col(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                "Query Protein Structure",
                                                width=6,
                                                className="text-center fw-bold",
                                                style=vis.border_column,
                                            ),
                                            dbc.Col(
                                                "Selected Protein Structure",
                                                className="text-center fw-bold",
                                                style=vis.border_column,
                                            ),
                                        ],
                                    ),
                                ]
                            ),
                        ],
                        align="end",
                        className="g-0 mt-3",
                        style=vis.border_row,
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    widgets.get_table_experiment_related_variants(),
                                ],
                                width=6,
                                className="p-1 dbc dbc-ag-grid",
                            ),
                            dbc.Col(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Div(id="id-exp-related-variants-protein-viewer"),
                                                ],
                                                width=6,
                                                style=vis.border_column,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Div(id="id-exp-related-variants-selected-protein-viewer"),
                                                ],
                                                style=vis.border_column,
                                            ),
                                        ],
                                        className="g-0 p-0",
                                    ),
                                ],
                                className="p-1",
                            ),
                        ],
                        className="mb-1",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(width=6),
                            dbc.Col(
                                [
                                    widgets.generate_label_with_info(
                                        label=gs.exp_seq_align_substitutions,
                                        id_info="id-exp-related-variants-selected-subs",
                                    )
                                ]
                            ),
                        ]
                    ),
                ],
            ),
        ],
        style={
            "box-shadow": "1px 2px 7px 0px grey",
            "border-radius": "5px",
            # "height": vis.related_variants_card_height,
        },
    )


def get_tab_experiment_related_variants():
    return html.Div(
        [
            # intro at the top
            html.H5("Search for related variants", className="page-title"),
            html.Div(
                html.P(gsh.exp_seq_align_blurb, className="px-5 text-primary text-wrap"),
            ),
            # form layout
            dbc.Row(
                [get_seq_align_form_exp()],
                className="mt-3",
                style={
                    "width": "70%",  # % width of the div
                    "margin": "0 auto",
                    # "border": "1px solid magenta",
                },
            ),
            html.Div(
                id="id-summary-exp-related-variants",
                className="d-flex justify-content-center",
            ),
            html.Div(
                id="id-alert-exp-related-variants",
                className="d-flex justify-content-center",
            ),
            # putting all this in a Div because it needs to appear after results are in
            dcc.Loading(
                overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                type="circle",
                color="var(--bs-secondary)",
                children=html.Div(
                    id="id-div-exp-related-variants",
                    style=vis.display_none,
                    children=[get_card_experiment_related_variants_result()],
                ),
                target_components={"id-table-exp-related-variants": "rowData"},
            ),
        ],
        className="mt-4",
    )


def get_layout():
    """This defines the tab layout."""
    return html.Div(
        [
            dcc.Tabs(
                [
                    # Experiment dashboard
                    dcc.Tab(
                        id="id-experiment-tab-1",
                        children=get_tab_experiment_main(),
                        label=gs.tab_1,
                        value="id-tab-exp-dash",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        children=get_tab_experiment_related_variants(),
                        label=gs.tab_2,
                        value="id-tab-exp-variants",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
                className="custom-tab-container",
                value="id-tab-exp-dash",
            )
        ],
        className=vis.main_page_class,
    )
