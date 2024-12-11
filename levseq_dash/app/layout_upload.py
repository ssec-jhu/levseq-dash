import dash_bootstrap_components as dbc
from dash import dcc, html

from levseq_dash.app import global_strings as gs

upload_form_layout = dbc.Form(
    [
        html.Br(),
        html.Br(),
        dbc.Row(
            [
                dbc.Label(gs.experiment_name, width=2),
                dbc.Col(
                    dbc.Input(type="text", id="id-input-experiment-name", placeholder=gs.experiment_name_placeholder),
                    width=10,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Substrate CAS Number", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text",
                        id="id-input-substrate-cas",
                        # TODO: place holder should be an example CAS number format
                        placeholder="Enter Substrate CAS Number",
                    ),
                    width=10,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Product CAS Number", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text",
                        id="id-input-product-cas",
                        placeholder="Enter Product CAS Number",
                    ),
                    width=10,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Assay", width=2),
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
                    width=10,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Technique", width=2),
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.RadioItems(
                                    options=[
                                        {
                                            "label": "EPR",
                                            "value": 1,
                                        },
                                        {
                                            "label": "SSM",
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
                    width=10,
                ),
            ],
            className="mb-3",
            style={"border": "1px solid #dee2e6"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Upload(
                        id="id-button-upload-experiment",
                        children=dbc.Button("Upload Experiment Data", color="primary"),
                        multiple=False,
                        style={
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "padding": "10px",
                            "textAlign": "center",
                            "cursor": "pointer",
                        },
                    ),
                    width=12,
                ),
            ],
            className="mb-3",
        ),
    ]
)
