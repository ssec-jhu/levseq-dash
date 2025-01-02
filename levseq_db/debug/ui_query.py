#
# ui_query.py
#
# Notes:
#  Defines a user interface for running predefined queries in the postgres database.
#

import flask
import dash
from dash import html, callback, dcc, dash_table, Input

import wsexec
from ui_base import UIbase


class UIquery(UIbase):

    def __init__(self):
        super().__init__(type(self).__name__)

        # CSS style for the DIV wrapper
        self.outerStyle = {
            "width": "100%",
            "back-color": "blue",
            "border": "solid",
            "border-width": "1px",
            "float": "left",
            "clear": "both",
        }

        # layout
        self.contents = [
            html.H3(id="h3_expt_stats_header", children="Data from experiment (not selected)"),
            html.Label(
                children="Query:", htmlFor="UIquery_dropdown::trigger", style={"display": "inline-block"}
            ),
            dcc.Dropdown(
                [],
                id="UIquery_dropdown::trigger",
                style={"width": "256px", "display": "inline-block"},
                optionHeight=20,
                disabled=True,
            ),
            dash_table.DataTable(
                id="tbl_query_result",
                data=[],
                page_size=5,
                style_cell={"font-size": "0.9em", "whiteSpace": "pre-line"},
            ),
        ]

        return

    # callback: query list dropdown selection
    @callback(
        Input("UIquery_dropdown::trigger", "value"),
        prevent_initial_call=True,
        on_error=UIbase.callbackException,
    )
    @staticmethod
    def callbackImpl(qs: str) -> None:
        print("UIquery_dropdown callback...")

        # copy the verb and parameters into the UI

        # execute the query TODO: PROBABLY A "Do it!" button with its own callback

        # update the DataTable component

        # # bind to a pandas DataFrame
        # df = pandas.DataFrame(data=rows, columns=cols)  # type:ignore

        # # we only want to see dates, not microseconds
        # df["dt_experiment"] = pandas.to_datetime(df["dt_experiment"]).dt.date
        # df["dt_load"] = pandas.to_datetime(df["dt_load"]).dt.date

        # update UI state
        dash.set_props("UIquery_dropdown::error", dict(value=""))

        # (we use dash.set_props instead of Output bindings)
        return None

    @staticmethod
    def RefreshTestQueryList() -> None:

        # get current user ID and group ID from session variables
        uid = flask.session["uid"]
        gid = flask.session["gid"]

        # enable the dropdown only if an experiment is selected
        ie = flask.session["iexpt"]
        if ie is None:
            dash.set_props("UIquery_dropdown::trigger", dict(data=[], disabled=True))
            return None

        # at this point we can get a list of queries to test
        eid, ename = flask.session["elist"][ie]
        cols, rows = wsexec.Query("get_test_queries", [eid, uid, gid])  # type:ignore
        iv = cols.index("verb")
        i1 = cols.index("param1")
        i2 = cols.index("param2")
        aOptions = [{"value": f"{r[iv]}&{r[i1]}&{r[i2]}", "label": f"{r[iv]}"} for r in rows]

        # refresh the dropdown list
        dash.set_props("UIquery_dropdown::trigger", dict(options=aOptions, disabled=False))

        return None
