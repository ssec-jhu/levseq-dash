#
# ui_expt_list.py
#
# Notes:
#  Defines a user interface for displaying a list of experiments.
#

import flask
import dash
from dash import html, callback, dash_table, Input
import pandas

import wsexec
from ui_base import UIbase
from ui_query import UIquery


class UIexptList(UIbase):

    def __init__(self):
        super().__init__(type(self).__name__)

        # CSS style for the DIV wrapper
        self.outerStyle = {
            "width": "100%",
            "float": "left",
            "clear": "both",
            "border-width": "4px 1px 1px 1px",
        }

        # layout
        self.contents = [
            html.H3(id="h3_expt_list_header", children="Experiments for user (not selected)"),
            dash_table.DataTable(
                id="UIexptList::trigger",
                data=[],
                page_size=5,
                row_selectable="single",
                style_cell={"font-size": "0.9em", "whiteSpace": "pre-line"},
                style_header={"background-color": "#f0f0f0", "font-weight": "bold"},
            ),
        ]

        return

    # callback: experiment list selection
    @callback(
        Input("UIexptList::trigger", "selected_rows"),
        prevent_initial_call=True,
        on_error=UIbase.callbackException,
    )
    @staticmethod
    def callbackImpl(selectedRows: list[int]) -> None:
        print("UIexptList callback...")

        # save the index of the selected row (or None if no row is selected)
        isSelected = isinstance(selectedRows, list) and len(selectedRows) > 0
        flask.session["iexpt"] = selectedRows[0] if isSelected else None

        # refresh the list of available test queries
        UIquery.RefreshTestQueryList()

        # (we use dash.set_props instead of Output bindings)
        return None

    @staticmethod
    def RefreshUserExperimentList() -> None:

        # get user ID and name from session variables
        uid = flask.session["uid"]
        uname = flask.session["uname"]

        # update UI state
        dash.set_props("h3_expt_list_header", dict(children=f"Experiments for user {uname} (ID {uid})"))
        dash.set_props("UIunloadData::error", dict(value=""))

        # query the database for a current list of experiments for the current user
        cols, rows = wsexec.Query("get_experiments_u", [uid])  # type:ignore

        # save a list of (ID, name) tuples for the experiment list
        iid = cols.index("eid")
        iname = cols.index("experiment_name")
        flask.session["elist"] = [(r[iid], r[iname]) for r in rows]

        # bind to a pandas DataFrame
        df = pandas.DataFrame(data=rows, columns=cols)  # type:ignore

        # we only want to see dates, not microseconds
        df["dt_experiment"] = pandas.to_datetime(df["dt_experiment"]).dt.date
        df["dt_load"] = pandas.to_datetime(df["dt_load"]).dt.date

        # refresh the DataTable UI
        dash.set_props("UIexptList::trigger", dict(data=df.to_dict("records")))

        # reset any selection in the displayed list of experiments
        dash.set_props("UIexptList::trigger", dict(selected_rows=[]))
        flask.session["iexpt"] = None

        return None
