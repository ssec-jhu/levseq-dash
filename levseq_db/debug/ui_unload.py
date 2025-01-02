#
# ui_unload.py
#
# Notes:
#  Defines a user interface for unloading experiment data from the database.
#

import flask
import dash
from dash import html, callback, Input

import wsexec
from ui_base import UIbase
from ui_expt_list import UIexptList


class UIunloadData(UIbase):

    def __init__(self):
        super().__init__(type(self).__name__)

        # CSS style for the DIV wrapper
        self.outerStyle = {
            "width": "fit-content",
            "border": "solid",
            "border-width": "1px",
            "float": "left",
        }

        # layout
        self.contents = [
            html.H3("Unload currently selected experiment"),
            html.Button("Zap!", id="UIunloadData::trigger", n_clicks=0, style={"width": "32px"}),
            html.Div(id="div_unload_experiment_info", children="(none)"),
        ]

        return

    # callback: zap button
    @callback(
        [Input("UIunloadData::trigger", "n_clicks")],
        prevent_initial_call=True,
        on_error=UIbase.callbackException,
    )
    @staticmethod
    def callbackImpl(n_clicks: int) -> None:
        print("UIunloadData callback...")

        # do nothing if no experiment is selected
        ie = flask.session["iexpt"]
        if ie is None:
            dash.set_props("div_unload_experiment_info", dict(children="(no experiment selected)"))
            return None

        # get current user ID and experiment ID from session variables
        uid = flask.session["uid"]
        eid, ename = flask.session["elist"][ie]

        # unload the experiment data and delete all assocated uploaded files
        wsexec.Query("unload_experiment", [uid, eid])

        # update UI state
        msg = f"Unloaded experiment ID {eid} ({ename})"
        dash.set_props("div_unload_experiment_info", dict(children=msg))
        dash.set_props("UIunloadData::error", dict(value=""))

        # refresh the user experiment list
        UIexptList.RefreshUserExperimentList()

        return None
