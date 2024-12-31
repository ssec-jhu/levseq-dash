#
# ui_set_metadata.py
#
# Notes:
#  Defines a user interface for entering metadata for an experiment.
#

import datetime

import flask
import dash
from dash import dcc, html, callback, Input, State

import wsexec
from ui_base import UIbase


class UIsetMetadata(UIbase):

    def __init__(self):
        super().__init__(type(self).__name__)

        # CSS style for the DIV wrapper
        self.outerStyle = {
            "width": "fit-content",
            "border": "solid",
            "border-width": "1px",
            "float": "left",
        }

        # dropdown list contents
        cols, rows = wsexec.Query("get_assays", [])  # type:ignore
        aAssays = [{"value": r[0], "label": r[1]} for r in rows]

        cols, rows = wsexec.Query("get_mutagenesis_methods", [])  # type:ignore
        aMutagenesisMethods = [{"value": r[0], "label": r[1]} for r in rows]

        # layout
        # fmt:off
        layout_ui_experiment_name = [
            html.Label("experiment name:", htmlFor="input_experiment_name"),
            dcc.Input(id="input_experiment_name", type="text", value="expt1", style={"width": "320px"}),
        ]

        layout_ui_experiment_date = [
            html.Label("experiment date:", htmlFor="input_experiment_date"),
            dcc.DatePickerSingle(
                id="input_experiment_date",
                min_date_allowed=datetime.date(2020, 1, 1),
                max_date_allowed=datetime.datetime.now(),
                initial_visible_month=datetime.datetime.today(),
                date=datetime.datetime.today(),
                # (see assets/main.py for CSS style)
        ),
        ]
        
        layout_ui_cas_substrate = [
            html.Label("CAS (substrate):", htmlFor="input_cascsv_substrate"),
            dcc.Input(id="input_cascsv_substrate", type="text", value="345905-97-7", style={"width": "160px"}),
        ]

        layout_ui_cas_product = [
            html.Label("CAS (product):", htmlFor="input_cascsv_product"),
            dcc.Input(id="input_cascsv_product", type="text", value="395683-37-1", style={"width": "160px"}),
        ]

        layout_ui_assay = [
            html.Label("assay technique:", htmlFor="input_assay"),
            dcc.Dropdown(aAssays, value=8, id="dropdown_assay", optionHeight=20),
        ]

        layout_ui_mutagenesis_method = [
            html.Label("mutagenesis method:", htmlFor="dropdown_mm"),
            dcc.Dropdown(aMutagenesisMethods, value=2, id="dropdown_mm", optionHeight=20),
        ]

        layout_ui_experiment_id = [
            html.Label("experiment ID:", htmlFor="div_eid", style={"display": "inline-block"}),
            html.Div(id="div_eid", children="(none yet)", style={"width":"128px", "display": "inline-block", "margin-left": "4px"}),
        ]
        # fmt:on

        self.contents = [
            html.H3("experiment metadata"),
            html.Div(id="div_experiment_name", children=layout_ui_experiment_name),
            html.Div(id="div_experiment_date", children=layout_ui_experiment_date),
            html.Div(id="div_cas_substrate", children=layout_ui_cas_substrate),
            html.Div(id="div_cas_product", children=layout_ui_cas_product),
            html.Div(id="div_assay", children=layout_ui_assay),
            html.Div(id="div_mutagenesis_method", children=layout_ui_mutagenesis_method),
            html.Button("Do it", id="UIsetMetadata::trigger", n_clicks=0),
            html.Div(id="div_experiment_id", children=layout_ui_experiment_id),
        ]

        return

        # callback: experiment metadata validation / get new experiment ID

    @callback(
        [Input("UIsetMetadata::trigger", "n_clicks")],
        [
            State("input_experiment_name", "value"),
            State("input_experiment_date", "date"),
            State("dropdown_assay", "value"),
            State("dropdown_mm", "value"),
            State("input_cascsv_substrate", "value"),
            State("input_cascsv_product", "value"),
        ],
        prevent_initial_call=True,
        on_error=UIbase.callbackException,
    )
    @staticmethod
    def callbackImpl(
        n_clicks: int,
        experimentName: str,
        experimentDate: str,
        assay: int,
        mutagenesis_method: int,
        cas_substrate: str,
        cas_product: str,
    ) -> None:
        print("UIsetMetadata callback")

        ### TODO: GET RID OF THIS HACK (SEE ui_set_user.py)
        if "uid" not in flask.session:
            flask.session["uid"] = 5

        # validate the user-entered experiment metadata and get a experiment ID
        eid = wsexec.Query(
            "init_load",
            [
                flask.session["uid"],
                experimentName,
                experimentDate,
                assay,
                mutagenesis_method,
                cas_substrate,
                cas_product,
            ],
        )  # type:ignore

        # update session variables
        flask.session["experiment_name"] = experimentName
        flask.session["eid"] = eid

        # update the UI state
        dash.set_props("div_eid", dict(children=str(eid)))
        dash.set_props("UIsetMetadata::error", dict(value=""))

        # (we use dash.set_props instead of Output bindings)
        return
