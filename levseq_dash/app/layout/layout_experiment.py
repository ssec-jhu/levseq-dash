import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import dcc, html

from levseq_dash.app import components, vis
from levseq_dash.app import global_strings as gs


def get_experiment_tab_dash():
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
                                                html.Div(
                                                    [
                                                        html.Span(gs.experiment, style=vis.experiment_info),
                                                        html.Span(id="id-experiment-name"),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Span(gs.date, style=vis.experiment_info),
                                                        html.Span(id="id-experiment-date"),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Span(gs.upload_date, style=vis.experiment_info),
                                                        html.Span(id="id-experiment-upload"),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Span(gs.technique, style=vis.experiment_info),
                                                        html.Span(id="id-experiment-mutagenesis-method"),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Span(gs.assay, style=vis.experiment_info),
                                                        html.Span(id="id-experiment-assay"),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Span(gs.technique, style=vis.experiment_info),
                                                        html.Span(id="id-experiment-mutagenesis-method"),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Span(gs.plates_count, style=vis.experiment_info),
                                                        html.Span(id="id-experiment-plate-count"),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Span(gs.smiles_file, style=vis.experiment_info),
                                                        html.Span(id="id-experiment-file-smiles"),
                                                    ]
                                                ),
                                            ]
                                        )
                                    ],
                                    className=vis.top_card_body,
                                ),
                            ],
                            style=vis.card_shadow,
                        ),
                        width=5,
                        style=vis.border_column,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(gs.reaction, className=vis.top_card_head),
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            components.create_layout_reaction(
                                                "id-experiment-reaction-image",
                                                "id-experiment-substrate",
                                                "id-experiment-product",
                                            )
                                        ),
                                    ],
                                    className=vis.top_card_body,
                                ),
                            ],
                            style=vis.card_shadow,
                        ),
                        style=vis.border_column,
                    ),
                ],
                className="mb-3",
            ),
            # top variants and viewer row
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
                                                [components.get_table_experiment_top_variants()],
                                                className="dbc dbc-ag-grid",
                                                # style=vis.border_table,
                                            )
                                        ],
                                        className="p-1 mt-3",  # fits to the card border
                                        # style={"height": "100%", "overflowX": "auto"}  # Allow content to expand
                                    ),
                                ],
                                # className="d-flex flex-column",  # Flexbox for vertical stacking
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
                                                [
                                                    html.Span(
                                                        [
                                                            dmc.Switch(
                                                                # thumbIcon=vis.icon_home,
                                                                id="id-switch-residue-view",
                                                                label=gs.view_all,
                                                                onLabel="ON",  # vis.icon_eye_open,
                                                                offLabel="OFF",  # vis.icon_eye_closed,
                                                                size="md",
                                                                className="custom-switch",
                                                                checked=False,
                                                            ),
                                                            components.get_info_icon_tooltip_bundle(
                                                                info_icon_id="id-switch-residue-view-info",
                                                                help_string="some help string",
                                                                location="top",
                                                            ),
                                                        ],
                                                        style={"display": "flex", "gap": "5px"},
                                                    )
                                                ],
                                                class_name="p-2",  # add some padding around the switch
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Card(
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        dbc.Label(gs.select_smiles),
                                                                        dcc.Dropdown(
                                                                            id="id-list-smiles-residue-highlight",
                                                                            disabled=True,
                                                                        ),
                                                                    ],
                                                                    width=3,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        dcc.RangeSlider(
                                                                            id="id-slider-ratio",
                                                                            value=[0.5, 1.5],
                                                                            min=0,
                                                                            step=0.1,
                                                                            tooltip={
                                                                                "always_visible": True,
                                                                                "placement": "bottom",
                                                                            },
                                                                            disabled=True,
                                                                            # className="dbc"
                                                                            className="custom-slider",
                                                                        ),
                                                                    ],
                                                                ),
                                                            ],
                                                            # removing the dbc.CardBody around this row also removes
                                                            # the padding. I am manually putting the padding back.
                                                            class_name="p-2 align-items-center",
                                                        )
                                                    )
                                                ],
                                                # if you justify the components to center then
                                                # the text overflows to the next row
                                                # justify="between",
                                                class_name="mt-3 mb-3 g-0 d-flex align-items-center",
                                                style=vis.border_row,
                                            ),
                                            dbc.Row(dbc.Col(components.get_protein_viewer())),
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
    return dbc.Container(
        [
            dbc.Row(
                [
                    components.get_label_fixed_for_form(gs.exp_seq_align_form_input, w=3),
                    # don't remove this dbc.Col, it creates a nice padding
                    dbc.Col(
                        [
                            html.Div(
                                id="id-input-exp-related-variants-query-sequence",
                                style={
                                    "width": "750px",
                                    "height": "100px",
                                    "whiteSpace": "normal",  # ensures wrapping
                                    "wordWrap": "break-word",  # breaks long words if needed
                                    "padding": "4px",
                                },
                                className="dbc text-muted",
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
                                id="id-input-exp-related-variants-threshold",
                                value=gs.seq_align_form_threshold_default,
                                type="text",
                                debounce=True,
                            ),
                        ],
                        width=3,
                    ),
                ],
                className="mb-1",
                style=vis.border_row,
            ),
            # dbc.Row(
            #     [
            #         components.get_label_fixed_for_form(gs.seq_align_form_hot_cold),
            #         dbc.Col(
            #             [
            #                 dbc.Input(
            #                     id="id-input-exp-related-variants-hot-cold",
            #                     value=gs.seq_align_form_hot_cold_n,
            #                     type="text",
            #                     debounce=True,
            #                 ),
            #             ],
            #             width=3,
            #         ),
            #     ],
            #     className="mb-1",
            #     style=vis.border_row,
            # ),
            dbc.Row(
                [
                    components.get_label_fixed_for_form(gs.exp_seq_align_residue),
                    dbc.Col(
                        [
                            dbc.Input(
                                id="id-input-exp-related-variants-residue",
                                type="text",
                                debounce=True,
                            )
                        ],
                        width=3,
                        align="center",
                    ),
                    dbc.Col(
                        [
                            components.get_info_icon_tooltip_bundle(
                                info_icon_id="id-exp-seq-align-info",
                                help_string=gs.exp_seq_align_residue_help,
                                location="top",
                            ),
                        ],
                        width=1,
                        align="center",
                        className="p-0",
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
        className="mt-3",
        style={
            "width": "60%",  # % width of the div
            "margin": "0 auto",
        },
    )


def get_experiment_tab_related_seq():
    return html.Div(
        [
            dbc.Row(html.P(gs.exp_seq_align_blurb)),
            dbc.Row(get_seq_align_form_exp()),
            html.Div(
                id="id-div-exp-related-variants-section",
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Related Experiments", className=vis.top_card_head),
                                            dbc.CardBody(
                                                [
                                                    dbc.Row(
                                                        [
                                                            html.P(
                                                                "TBD: (placeholder) We need some instructions "
                                                                "here for "
                                                                "the user, on what are they are seeing and "
                                                                "to know that they can click on a row...."
                                                            )
                                                        ],
                                                        className="mt-3",  # fits to the card border
                                                    ),
                                                    dbc.Row(
                                                        [components.get_table_experiment_related_variants()],
                                                        className="dbc dbc-ag-grid mt-3",
                                                    ),
                                                ],
                                                className="p-1 mt-3",  # fits to the card border
                                            ),
                                        ],
                                        className="d-flex flex-column",  # Flexbox for vertical stacking
                                        style={
                                            "box-shadow": "1px 2px 7px 0px grey",
                                            "border-radius": "5px",
                                            "height": vis.related_variants_card_height,
                                        },
                                    ),
                                ],
                                width=6,
                                style=vis.border_column,
                                # remove all gutters from the col to snap to the card
                                # className="g-3"
                            ),
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(
                                                " Query Protein vs. Selected Protein Substitutions",
                                                className=vis.top_card_head,
                                            ),
                                            dbc.CardBody(
                                                [
                                                    # experiment id of the comparison
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    components.generate_label_with_info(
                                                                        label="Query Experiment ID: ",
                                                                        id_info="id-exp-related-variants-id",
                                                                    )
                                                                ],
                                                                className="text-center",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    components.generate_label_with_info(
                                                                        label="Selected Experiment ID: ",
                                                                        id_info="id-exp-related-variants-selected-id",
                                                                    )
                                                                ],
                                                                className="text-center",
                                                            ),
                                                        ],
                                                        className="mb-3",
                                                    ),
                                                    # reaction image and the substrate and product
                                                    # strings of the comparison
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    components.create_layout_reaction(
                                                                        "id-exp-related-variants-reaction-image",
                                                                        "id-exp-related-variants-substrate",
                                                                        "id-exp-related-variants-product",
                                                                    )
                                                                ],
                                                                className="text-center",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    components.create_layout_reaction(
                                                                        "id-exp-related-variants-selected-reaction-image",
                                                                        "id-exp-related-variants-selected-substrate",
                                                                        "id-exp-related-variants-selected-product",
                                                                    )
                                                                ],
                                                                className="text-center",
                                                            ),
                                                        ],
                                                        className="mb-3",
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    html.Div(
                                                                        id="id-exp-related-variants-protein-viewer"
                                                                    ),
                                                                ],
                                                                width=6,
                                                                className="text-center",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    html.Div(
                                                                        id="id-exp-related-variants-selected-protein-viewer"
                                                                    ),
                                                                ],
                                                                className="text-center",
                                                            ),
                                                        ],
                                                        className="p-0 mb-3",
                                                    ),
                                                    # specify the substitutions that are being visualized
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    components.generate_label_with_info(
                                                                        label="Selected Substitutions: ",
                                                                        id_info="id-exp-related-variants-selected-subs",
                                                                    )
                                                                ]
                                                            )
                                                        ],
                                                        className="justify-content-center",
                                                    ),
                                                ],
                                                className="p-1 mt-3",
                                            ),
                                        ],
                                        style={
                                            "box-shadow": "1px 2px 7px 0px grey",
                                            "border-radius": "5px",
                                            # Leave this commented so the card height
                                            # can grow since there are dynamic components in it
                                            # "height": vis.related_variants_card_height,
                                        },
                                    )
                                ],
                                width=6,
                            ),
                        ]
                    ),
                ],  # html.Div
            ),
        ],
        className="mt-4",
    )


def get_experiment_page():
    """This defines the tab layout."""
    return html.Div(
        [
            # dbc.Tabs(
            #     [
            #         # Experiment dashboard
            #         dbc.Tab(
            #             get_experiment_tab_dash(),
            #             label=gs.tab_1,
            #             activeTabClassName="fw-bold",
            #             tab_id="id-tab-exp-dash",
            #         ),
            #         # Gene Expression Query Tab
            #         dbc.Tab(
            #             get_experiment_tab_related_seq(),
            #             label=gs.tab_2,
            #             activeTabClassName="fw-bold",
            #             # tab_id="id-tab-horizontal-bootstrap-geq",
            #         ),
            #     ],
            #     active_tab="id-tab-exp-dash",
            #     className="dbc nav-fill",  # Use Bootstrap's nav-fill class to fill the tab_horizontal_bootstrap space
            # )
            # TODO: replacing dbc.tabs with dcc ones as they created a glitch when dockerized!
            # debug this later or add better styling
            dcc.Tabs(
                [
                    # Experiment dashboard
                    dcc.Tab(
                        get_experiment_tab_dash(),
                        label=gs.tab_1,
                        value="id-tab-exp-dash",
                    ),
                    # Gene Expression Query Tab
                    dcc.Tab(
                        get_experiment_tab_related_seq(),
                        label=gs.tab_2,
                        value="id-tab-exp-variants",
                    ),
                ],
                value="id-tab-exp-dash",
                className="dbc nav-fill",  # Use Bootstrap's nav-fill class to fill the tab_horizontal_bootstrap space
            )
        ]
    )
