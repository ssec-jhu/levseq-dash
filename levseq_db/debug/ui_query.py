#
# ui_query.py
#
# Notes:
#  Defines a user interface for running predefined queries in the postgres database.
#

import flask
import dash
from dash import html, callback, dcc, dash_table, Input, State
import pandas

import wsexec
from ui_base import UIbase


class UIquery(UIbase):

    def __init__(self):
        super().__init__(type(self).__name__)

        # CSS style for the DIV wrapper
        self.outerStyle = {
            "width": "100%",
            "float": "left",
            "clear": "both",
        }

        # layout
        self.params_input = [
            html.Label(
                children="Query:",
                htmlFor="UIquery--dropdown::trigger",
                style={
                    "float": "left",
                    "margin-right": "4px",
                },
            ),
            dcc.Dropdown(
                [],
                id="UIquery--dropdown::trigger",
                style={
                    "width": "256px",
                    "float": "left",
                    "vertical-align": "top",
                },
                optionHeight=20,
                disabled=True,
            ),
            html.Label(
                "param 1:",
                htmlFor="UIquery_param1",
                style={"vertical-align": "top", "margin": "0px 4px 0px 16px"},
            ),
            dcc.Input(id="UIquery_param1", type="text", value="", style={"width": "64px"}),
            html.Label(
                "param 2:",
                htmlFor="UIquery_param2",
                style={"vertical-align": "top", "margin": "0px 4px 0px 16px"},
            ),
            dcc.Input(id="UIquery_param2", type="text", value="", style={"width": "64px"}),
            html.Button(
                "Do it!",
                id="UIquery--btn::trigger",
                n_clicks=0,
                style={"width": "64px", "margin-left": "16px"},
                disabled=True,
            ),
        ]

        self.tbl = [
            dash_table.DataTable(
                id="UIquery_result_set",
                data=[],
                page_size=5,
                style_header={"background-color": "#f0f0f0", "font-weight": "bold"},
                style_cell={"font-size": "0.9em", "white-space": "pre-line"},
                style_table={
                    "display": "inline-block",
                    "float": "left",
                    "clear": "both",
                },
            ),
        ]

        self.contents = [
            html.H3(id="h3_expt_stats_header", children="Test queries"),
            html.Div(
                children=self.params_input,
                style=dict(display="inline-block", clear="both", margin="0px 0px 4px 0px"),
            ),
            html.Div(children=self.tbl, style={"width": "fit-content"}),
        ]

        return

    # callback: query list dropdown selection
    @callback(
        Input("UIquery--dropdown::trigger", "value"),
        prevent_initial_call=True,
        on_error=UIbase.callbackException,
    )
    @staticmethod
    def callbackImpl_dropdown(qs: str) -> None:
        print("UIquery--dropdown callback...")

        if qs is None:
            return None

        # copy the verb and parameters into the UI
        aqs = qs.split("&")
        flask.session["verb"] = aqs[0]
        val = aqs[1] if aqs[1] != "None" else ""
        dash.set_props("UIquery_param1", dict(value=val, disabled=(val == "")))
        val = aqs[2] if aqs[2] != "None" else ""
        dash.set_props("UIquery_param2", dict(value=val, disabled=(val == "")))
        dash.set_props("UIquery--btn::trigger", dict(disabled=False))

        # clear the DataTable component
        dash.set_props("UIquery_result_set", dict(data=[]))

        # update UI state
        dash.set_props("UIquery::error", dict(value=""))

        # (we use dash.set_props instead of Output bindings)
        return None

    # callback: query button click
    @callback(
        [Input("UIquery--btn::trigger", "n_clicks")],
        [State("UIquery_param1", "value"), State("UIquery_param2", "value")],
        prevent_initial_call=True,
        on_error=UIbase.callbackException,
    )
    @staticmethod
    def callbackImpl_button(n_clicks: int, sParam1: str, sParam2: str) -> None:
        print("UIquery--btn callback...")

        # get the "verb"
        if "verb" not in flask.session:
            return None

        verb = flask.session["verb"]

        # get the parameter values as integers
        if sParam1 != "":
            params = [int(sParam1) if sParam1.isnumeric() else sParam1]

            if sParam2 != "":
                params += [int(sParam2) if sParam2.isnumeric() else sParam2]
        else:
            params = []

        # execute the query
        cols, rows = wsexec.Query(verb, params)  # type:ignore

        # bind to a pandas DataFrame
        df = pandas.DataFrame(data=rows, columns=cols)  # type:ignore

        # we only want to see dates, not microseconds, so
        #  it might be worth doing some kind of foreach to find date columns
        # df["dt_experiment"] = pandas.to_datetime(df["dt_experiment"]).dt.date

        dash.set_props("UIquery_result_set", dict(data=df.to_dict("records")))

        # update UI state
        dash.set_props("UIquery::error", dict(value=""))

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
            dash.set_props("UIquery--dropdown::trigger", dict(data=[], disabled=True))
            dash.set_props("UIquery_param1", dict(value="", disabled=True))
            dash.set_props("UIquery_param2", dict(value="", disabled=True))
            dash.set_props("UIquery--btn::trigger", dict(disabled=False))
            return None

        # at this point we can get a list of queries to test
        eid, ename = flask.session["elist"][ie]
        cols, rows = wsexec.Query("get_test_queries", [eid, uid, gid])  # type:ignore
        iv = cols.index("verb")
        i1 = cols.index("param1")
        i2 = cols.index("param2")
        aOptions = [{"value": f"{r[iv]}&{r[i1]}&{r[i2]}", "label": f"{r[iv]}"} for r in rows]

        # refresh the dropdown list
        dash.set_props("UIquery--dropdown::trigger", dict(options=aOptions, disabled=False))

        return None
