import dash_bootstrap_components as dbc
from dash import dcc, html

from levseq_dash.app import global_strings as gs
from levseq_dash.app.components import vis, widgets
from levseq_dash.app.data_manager.experiment import MutagenesisMethod

# TODO: all placeholders must be in strings file


def get_form():
    return dbc.Form(
        [
            html.Br(),
            html.Br(),
            dbc.Row(
                [
                    widgets.get_label_fixed_for_form(gs.experiment_name),
                    dbc.Col(
                        dbc.Input(
                            type="text",
                            id="id-input-experiment-name",
                            placeholder=gs.experiment_name_placeholder,
                            debounce=True,
                        ),
                    ),
                ],
                className="mb-1",
            ),
            dbc.Row(
                [
                    widgets.get_label_fixed_for_form(gs.experiment_date),
                    dbc.Col(
                        [
                            dcc.DatePickerSingle(
                                id="id-input-experiment-date",
                                clearable=True,
                                # className="dbc",
                                # TODO: what should be the placeholder
                                # placeholder="date of experiment"
                            )
                        ],
                    ),
                ],
                className="mb-1",
            ),
            dbc.Row(
                [
                    widgets.get_label_fixed_for_form(gs.substrate_smiles_input),
                    dbc.Col(
                        dbc.Textarea(
                            # type="text",
                            id="id-input-substrate",
                            placeholder=gs.smiles_input_placeholder,
                            invalid=True,
                            # need to remove debounce
                            # smiles string needs to be verified on demand
                            # debounce=True,
                        ),
                    ),
                ],
                className="mb-1",
            ),
            dbc.Row(
                [
                    widgets.get_label_fixed_for_form(gs.product_smiles_input),
                    dbc.Col(
                        dbc.Textarea(
                            # type="text",
                            id="id-input-product",
                            placeholder=gs.smiles_input_placeholder,
                            invalid=True,
                            # need to remove debounce
                            # smiles string needs to be verified on demand
                            # debounce=True,
                        ),
                    ),
                ],
                className="mb-1",
            ),
            dbc.Row(
                [
                    widgets.get_label_fixed_for_form(gs.assay),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="id-list-assay",
                                        placeholder="Select Assay Technique.",
                                    ),
                                ],
                                className="dbc",
                            ),
                        ]
                    ),
                ],
                className="mb-1",
            ),
            dbc.Row(
                [
                    widgets.get_label_fixed_for_form(gs.tech),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    dbc.RadioItems(
                                        options=[MutagenesisMethod.epPCR, MutagenesisMethod.SSM],
                                        value=MutagenesisMethod.epPCR,
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
            ),
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Upload(
                            id="id-button-upload-data",
                            children=dbc.Button(gs.button_upload_csv, color="secondary", outline=True),
                            multiple=False,
                            style=vis.upload_default,
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dcc.Upload(
                            id="id-button-upload-structure",
                            children=dbc.Button(gs.button_upload_pdb, color="secondary", outline=True),
                            multiple=False,
                            style=vis.upload_default,
                        ),
                        width=6,
                    ),
                ],
                className="mb-1",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            id="id-button-upload-data-info",
                            style={
                                "word-break": "break-all",  # allows breaking between any characters
                                "whiteSpace": "normal",  # enables wrapping
                                "width": "100%",  # ensure it fits container
                            },
                        ),
                        width=6,
                    ),
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
                            # submit button will start out disabled until all files are uploaded and verified
                            disabled="True",
                        ),
                        width=6,
                        className="d-grid gap-2 col-12 mx-auto",
                    ),
                ],
                className="mb-3",
            ),
            html.Div(
                id="id-alert-upload",
                className="d-flex justify-content-center",
            ),
        ]
    )


layout = html.Div(
    [get_form()],
    style={
        "width": "70%",  # 50% width
        "margin": "0 auto",  # Center horizontally
        # "text-align": "center",  # Center text inside the div
        # "border": "1px solid black",  # for visual debugging
        # "padding": "10px",  #spacing inside the div
    },
)
