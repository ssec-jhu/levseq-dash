#
# ui_set_user.py
#
# Notes:
#  Defines a user interface for setting the current LevSeq user.
#

import flask
import dash
from dash import dcc, html, callback, Input
import pandas

import wsexec
from ui_base import UIbase


class UIsetUser(UIbase):

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
        cols, rows = wsexec.Query("get_usernames", [])  # type:ignore
        iv = cols.index("uid")
        iu = cols.index("username")
        ig = cols.index("groupname")
        aUsers = [{"value": r[iv], "label": f"{r[iu]} ({r[ig]})"} for r in rows]

        # layout
        self.contents = [
            html.H3("Select LevSeqUser"),
            dcc.Dropdown(aUsers, id="UIsetUser::trigger", style={"width": "160px"}),
            html.Label("Current user ID:", htmlFor="div_uid", style={"display": "inline-block"}),
            html.Div(
                id="div_uid",
                children="(not selected)",
                style={"display": "inline-block", "margin-left": "4px"},
            ),
        ]

        return

    # callback: user list dropdown selection
    @callback(
        Input("UIsetUser::trigger", "value"),
        prevent_initial_call=True,
        on_error=UIbase.callbackException,
    )
    @staticmethod
    def callbackImpl(uid) -> None:
        print("UIsetUser callback...")

        # do nothing if the user-selection dropdown has no current value
        if uid is None:
            msg = "(not selected)"

        else:

            if flask.has_request_context():
                remoteIPaddr = str(flask.request.remote_addr)
                flask.session["uid"] = uid
            else:  # (this should not happen)
                remoteIPaddr = "?.?.?.?"

            # save the IP address in the database table of users
            wsexec.Query("save_user_ip", [uid, remoteIPaddr])

            # get user session config
            cols, rows = wsexec.Query("get_user_info", [uid])  # type:ignore
            flask.session["groupname"] = rows[0][cols.index("groupname")]
            msg = str(uid)

        # update UI state
        dash.set_props("div_uid", dict(children=msg))

        # refresh the user experiment list
        cols, rows = wsexec.Query("get_user_experiments", [uid])  # type:ignore
        df = pandas.DataFrame(data=rows, columns=cols)  # type:ignore
        dash.set_props("tbl_experiment_list", dict(selected_rows=[]))
        dash.set_props("tbl_experiment_list", dict(data=df.to_dict("records")))
        dash.set_props("UIunloadData::error", dict(value=""))

        # (we use dash.set_props instead of Output bindings)
        return
