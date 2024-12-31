#
# ui_unload.py
#
# Notes:
#  Defines a user interface for unloading experiment data from the database.
#

import flask
import dash
from dash import html, dash_table, callback, Input, State
import pandas

import wsexec
from ui_base import UIbase


class UIunloadData(UIbase):

    def __init__(self):
        super().__init__(type(self).__name__)

        # CSS style for the DIV wrapper
        self.outerStyle = {
            "width": "100%",
            "border": "solid",
            "border-width": "1px",
            "float": "left",
            "clear": "both",
        }

        # layout
        self.contents = [
            html.H3("Unload experiment"),
            dash_table.DataTable(
                id="tbl_experiment_list",
                data=[],
                page_size=5,
                row_selectable="single",
                style_cell={"font-size": "0.9em"},
            ),
            html.Button("Zap!", id="UIunloadData::trigger", n_clicks=0, style={"width": "32px"}),
            html.Div(id="div_unload_experiment_info", children="(none)"),
        ]

        return

    # callback: zap button
    @callback(
        [Input("UIunloadData::trigger", "n_clicks")],
        [State("tbl_experiment_list", "selected_row_ids")],
        prevent_initial_call=True,
        on_error=UIbase.callbackException,
    )
    @staticmethod
    def callbackImpl(n_clicks: int, selectedRowIds: list[int]) -> None:
        print("UIunloadData callback...")

        uid = flask.session["uid"]

        if not isinstance(selectedRowIds, list) or len(selectedRowIds) == 0:
            dash.set_props("div_unload_experiment_info", dict(children="(no experiment selected)"))
            return None

        # at this point we assume that the user has selected an experiment to unload
        eid = selectedRowIds[0]  # (the DataTable component returns the "id" column value here)

        # unload the experiment data and delete all assocated uploaded files
        wsexec.Query("unload_experiment", [uid, eid])

        # update UI state
        ename = "???"
        msg = f"Unloaded experiment ID {eid} ({ename})"
        dash.set_props("div_unload_experiment_info", dict(children=msg))
        dash.set_props("UIunloadData::error", dict(value=""))

        # refresh the user experiment list
        cols, rows = wsexec.Query("get_user_experiments", [uid])  # type:ignore
        df = pandas.DataFrame(data=rows, columns=cols)  # type:ignore
        dash.set_props("tbl_experiment_list", dict(selected_rows=[]))
        dash.set_props("tbl_experiment_list", dict(data=df.to_dict("records")))

        # update session state
        flask.session["eid"] = None
        flask.session["experiment_name"] = None

        return None
