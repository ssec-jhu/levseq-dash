import dash_bootstrap_components as dbc
from dash import dcc, html

from levseq_dash.app import components, inline_styles
from levseq_dash.app import global_strings as gs

# TODO: all placeholders must be in strings file

form = dbc.Form(
    [
        html.Br(),
        html.Br(),
        dbc.Row(
            [
                components.get_label(gs.experiment_name),
                dbc.Col(
                    dbc.Input(
                        type="text",
                        id="id-input-experiment-name",
                        placeholder=gs.experiment_name_placeholder,
                        debounce=True,
                    ),
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                components.get_label(gs.experiment_date),
                dbc.Col(
                    [
                        dcc.DatePickerSingle(
                            id="id-experiment-date",
                            clearable=True,
                            # className="dbc",
                            # TODO: what should be the placeholder
                            # placeholder="date of experiment"
                        )
                    ],
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                components.get_label(gs.substrate_cas),
                dbc.Col(
                    dbc.Input(
                        type="text",
                        id="id-input-substrate-cas",
                        # TODO: place holder should be an example CAS number format
                        placeholder="Enter Substrate CAS Number",
                        debounce=True,
                    ),
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                components.get_label(gs.product_cas),
                dbc.Col(
                    dbc.Input(
                        type="text",
                        id="id-input-product-cas",
                        placeholder="Enter Product CAS Number",
                        debounce=True,
                    ),
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                components.get_label(gs.assay),
                dbc.Col(
                    dcc.Dropdown(
                        id="id-list-assay",
                        options=[
                            {"label": "Option 1", "value": "1"},
                            {"label": "Option 2", "value": "2"},
                            {"label": "Option 3", "value": "3"},
                        ],
                        placeholder="Select Assay Technique.",
                    ),
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                components.get_label(gs.tech),
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.RadioItems(
                                    options=[
                                        {
                                            "label": gs.eppcr,
                                            "value": 1,
                                        },
                                        {
                                            "label": gs.ssm,
                                            "value": 2,
                                        },
                                    ],
                                    value=1,
                                    id="id-radio-epr",
                                    inline=True,
                                ),
                            ],
                            style={"display": "flex", "flexDirection": "row", "alignItems": "left", "gap": "20px"},
                        )
                    ],
                    align="center",
                    # className="d-flex justify-content-center",
                ),
            ],
            className="mb-3",
            # style={"border": "1px solid #dee2e6"},
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Upload(
                        id="id-button-upload-data",
                        children=dbc.Button(gs.button_upload_csv, color="secondary", outline=True),
                        multiple=False,
                        style=inline_styles.upload_default,
                    ),
                    width=6,
                ),
                dbc.Col(
                    dcc.Upload(
                        id="id-button-upload-structure",
                        children=dbc.Button(gs.button_upload_pdb, color="secondary", outline=True),
                        multiple=False,
                        style=inline_styles.upload_default,
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(html.Div(id="id-button-upload-data-info"), width=6),
                dbc.Col(html.Div(id="id-button-upload-structure-info"), width=6),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        id="id-button-submit",
                        n_clicks=0,
                        class_name="btn-primary",
                        size="md",
                        children="Submit",
                        # disabled="True",  # TODO: must be disabled at first
                    ),
                    width=6,
                    className="d-grid gap-2 col-12 mx-auto",
                ),
            ],
            className="mb-3",
        ),
    ]
)

upload_form_layout = html.Div(
    [form],
    style={
        "width": "70%",  # 50% width
        "margin": "0 auto",  # Center horizontally
        # "text-align": "center",  # Center text inside the div
        # "border": "1px solid black",  # for visual debugging
        # "padding": "10px",  #spacing inside the div
    },
)
